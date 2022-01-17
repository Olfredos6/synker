from django.db import models
from pathlib import Path
from django.conf import settings
import subprocess
from datetime import datetime, timedelta
from os import environ, stat
from pytz import utc as UTC
import glob
from time import sleep, time 
import uuid
import random
from sync_utils.github import get_issues, post_new_issue


class Student(models.Model):
    customer_no = models.IntegerField(primary_key=True)
    surname = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    email = models.CharField(max_length=150)


class Repo(models.Model):
    date_added = models.DateTimeField(auto_now_add=True, null=True)
    node_id = models.CharField(max_length=32, null=False, primary_key=True)
    student = models.ForeignKey(Student, related_name="st_owner", on_delete=models.PROTECT, null=True)
    type = models.CharField(max_length=10, null=False)
    _name = models.CharField(max_length=100, null=True)
    full_name = models.CharField(max_length=100)
    updated_at = models.DateTimeField(null=True)
    url = models.URLField(max_length=10, null=False)
    clone_url = models.URLField(max_length=10, null=False)
    size = models.IntegerField()
    owner_login = models.CharField(max_length=100, null=False)
    student = models.ForeignKey(Student, related_name="student", on_delete=models.PROTECT, null=True)
    open_count = models.IntegerField(default=0)

    @property
    def name(self):
        '''
            Returns repo name. if _name is null, computes it
            from full_name
        '''
        if self._name:
            return self._name
        else:
            x = self.full_name
            return x[x.index("/")+1:]

    @staticmethod
    def recent_populars():
        return Repo.objects.all().order_by('-updated_at', '-open_count')[:5]

    @staticmethod
    def create_from_payload(type, **kwargs):
        '''
            Simplifies creating Repo objects using GitHub's repository payload
        '''
        # print(kwargs)
        new_repo = Repo()
        new_repo.type = type
        new_repo.node_id = kwargs.get('node_id')
        new_repo._name = kwargs.get('name')
        new_repo.full_name = kwargs.get('full_name')
        new_repo.updated_at = kwargs.get('pushed_at') # based on the difference between pushed_at and updated_at https://stackoverflow.com/a/15922637/5253580
        new_repo.clone_url = kwargs.get('clone_url')
        new_repo.size = kwargs.get('size')
        new_repo.owner_login = kwargs.get('owner').get('login')
        new_repo.save()
        return new_repo
    
    @staticmethod
    def check_update():
        ''' 
            For each known repos URL, check if the repo
            pushed_at timstamp has changed. If so, sync the repo.
        '''
        pass

    @property
    def path(self):
        ''' returns the repo directory path '''
        return settings.SYNKER_REPO_DIR.joinpath(self.node_id)

    @property
    def short(self):
        return self.node_id[-10:][:-1]
    
    @property
    def folder_name(self):
        ''' Valid name to use for code-server '''
        return f"{self.owner_login}__{self.name}"

    def update_db(self, **payload):
        '''
            Updates the repo's data on the databse. 
            For now, the most important piece of information
            requiring an update is the updated_at timestamp. 
            This info is updated everytime the repo is pulled.
        '''
        print("Received size ---->", self.full_name, payload.get('size'))
        return Repo.objects.filter(node_id=self.node_id).update(
            # updated_at=payload.get('updated_at')
            **payload
        )

    def set_student(self, student: Student):
        '''
            sets repo's student and returns updated repo object
        '''
        Repo.objects.filter(node_id=self.node_id).update(student=student)
        return Repo.objects.get(node_id=self.node_id)

    # # OVERRIDDEN
    # def delete(self, *args, **kwargs):
    #     '''
    #         Deleting a repository necessitates removing its folder as well.
    #     '''


    ## GIT TIGHT Methods
    def run_cmd(self, cmd: list)-> str:
        '''
            A general way for running commands on
            a repo's directory. 
            One of the justification is that we will always
            need to make sure that we are in the right directory before
            executing for instance a git command on a repo 
        '''
        process = subprocess.run(cmd, capture_output=True, cwd=self.path)
        return process.stdout.decode("utf-8")

    def clone(self):
        ''' clone the repo using git's clone command '''
        # insert GitHub's auth_token inot repo's clone URL
        authed_url = self.clone_url.replace("github.com", f"{environ.get('GITHUB_TOKEN')}@github.com")
        # print("New URL", authed_url)
        # cloning_proc = subprocess.run(['git', 'clone', authed_url, self.path ], capture_output=True)
        # print(cloning_proc, cloning_proc.stdout)
        print(self.run_cmd(['git', 'clone', authed_url, self.path ]))

    def pull(self):
        ''' git pull on the repo 
            @TODO ensure we can monitor weither this operation was
            successfull or not. Perhaps a git pull flag?
        '''
        print(self.run_cmd((['git', 'pull', '--allow-unrelated-histories'])))

    @property
    def branches(self):
        return [ b.strip() for b in self.run_cmd(["git","branch","--list","-a"]).split("\n ")]

    @property
    def branch(self):
        '''returns current branch'''
        return self.run_cmd(["git", "branch"]).replace("* ", "").replace("\n", "")
    
    def checkout(self, branch_name:str):
        '''
            Allows switching between branches
        '''
        # first check if branch exists
        if branch_name not in self.branches:
            raise ValueError(f"Branch {branch_name} does not exist")

        # check if repo was edited, if true, reset it first
        if self.was_edited:
            self.reset()
        
        return self.run_cmd(["git", "checkout", branch_name])
        

    @property
    def was_edited(self):
        '''
            Excutes git status on the repo to check if it has been edited.
            If yes, return True, else False 
        '''
        # st_proc = subprocess.run(['git', 'status', '--porcelain'], capture_output=True, cwd=self.path)
        r = self.run_cmd(['git', 'status', '--porcelain'])
        if r == "":
            return False
        else:
            return True
    
    def reset(self):
        '''
            Repo git reset --hard
        '''
        print(self.run_cmd(["git", "reset", "--hard"]))

    def sync(self, timestamp:datetime = None, size=None)-> None:
        '''
        Syncs a repository. 
        Starts by checking if the repos folder contains a repo that matches this repo's GitHub node_id
            creates it if necessay.
        If the repo is created
            use git clone. 
            Otherwwise, check if the updated_at are different.
                If different, git pull
        
        Accepts:
            timestamp: a datetime.
                    Using this argument forces aplying git clone on the repo.

                    Defaults to self.updated_at
        
        Returns: 0 if not updated
                 1 if updated
                 2 if cloned   
        '''
        feedback = 0
        if not timestamp:
            timestamp = self.updated_at
        
        # print(f"Syncing {self.full_name} using timestamp {timestamp}")
        created_repo = False
        if not self.path.exists():
            self.path.mkdir()
            created_repo = True
        else:
            # print("repo folder exists, updating...")
            pass
        
        if created_repo:
            # git clone
            # print(f"Cloning {self.full_name} into {self.path}")
            self.clone()
            self.update_db(updated_at=timestamp)
            feedback = 2

        else:
            # print(f"will only update if {self.updated_at} is greater than {timestamp.replace(tzinfo=UTC)}")
            if self.updated_at < timestamp.replace(tzinfo=UTC):
                # print(f"Updating/pulling {self.full_name}")
                # first check if the repo was edited locally, reset it if necessary
                if self.was_edited:
                    self.reset()

                self.pull()
                self.update_db(updated_at=timestamp, size=size)
                feedback = 1
        
        return feedback
    
    ## .GIT TIGHT Methods

    def track(self) -> None:
        ''' saves repo data to the db,
            marking the repo is now tracked
        '''
        pass

    def dir_struct(self) -> dict:
        ''' returns a dictionary object representing the 
            the folder structure of the repo. We only go 3 level down.
        '''
        from os import scandir

        def traverse(path, parent):
            ''' traverse dir at path to form a structure inside
                parent and return the updated parent
            '''
            # print(f"Traversing {path}")
            for entry in scandir(path):
                parent["-"] = [] # will list files 
                if entry.is_dir():
                    parent[entry.name] = {"-": []}
                    traverse(entry, parent[entry.name])
                else:
                    parent.get("-").append(entry.name)
            
            return parent
        
        return traverse(self.path,{"-": []})

    def find_file_update(self, filename, content):
        '''
            Searches for a file in the repo's directory
            and if found, updates its content with the 
            given content.
        '''
        file = glob.glob(f"{self.path}/**/{filename}", recursive=True )
        if not file:
            return False
        else:
            print("updatinf file at", file[0])
            with open(file[0], 'w') as f:
                f.write(content)
            return True

    def get_code_server(self):
        '''
            Starts a code-server instance and/or returns the port on
            which the server runs.

            Only the ports ranging from 4005 to 4010 are used.
            @TODO:
                Better management, better provisioning....
        '''
        print(CodeServerPort.objects.all())
        from core.utils import start_code_server_instance
        port = CodeServerPort.provision(self.folder_name)
        # we must wait a lil here
        print("Wainting 5 seconds...")
        sleep(5) # I do not like this but we do this for now
        print("Starting new instance after 5 seconds...")
        # @TODO Wainting 5 seconds is not enough....no gurantee given
        start_code_server_instance(port, self.path, self.folder_name)

        return port
    
    def kill_code_server(self):
        from core.utils import kill_code_server_instance
        kill_code_server_instance(self.folder_name)
        CodeServerPort.objects.get(container=self.folder_name).delete()

    def update_remote_token_access(self):
        ''' 
            Helper method to update the token access as specified on the remote URL
            if it is ever updated from the configuration files.
        '''
        return self.run_cmd(["git", "remote", "set-url", "origin", self.clone_url.replace("https://", f"https://{settings.API_KEY}@" )])

    def create_issue(self, title, body):
        return post_new_issue(self.owner_login, self._name, { "title": title, "body": body})

    def get_open_issues(self):
        return get_issues(*self.full_name.split("/"))

    def increment_open_count(self):
        print("Updating open count", Repo.objects.filter(node_id=self.node_id).update(open_count=models.F('open_count')+1))


class CodeServerPort(models.Model):
    # Port manager for code-server instances
    date_assigned = models.DateTimeField(auto_now_add=True, null=True)
    number = models.IntegerField(primary_key=True)
    container = models.CharField(max_length=15, null=True)

    @staticmethod
    def free_one():
        # returns an unused port between 4005 and 4015
        free_ports = [ number for number in range(4005, 4011) if number not in [port.number for port in CodeServerPort.objects.all()] ]
        print("Found FREE PORTS", free_ports)
        if len(free_ports) == 0:
            # kill the oldest and return its number
            oldest = CodeServerPort.objects.all().order_by('date_assigned')
            print("Found PORTS in use")
            for i in oldest:
                print(i.date_assigned, i.container, i.number)
            
            oldest = oldest[0]
            port = oldest.number

            oldest.destroy()
            from core.utils import kill_code_server_instance
            kill_code_server_instance(oldest.container)

            oldest.delete()
            return port

        else: 
            return free_ports[0]
    

    @staticmethod
    def kill(container_name):
        from core.utils import kill_code_server_instance
        kill_code_server_instance(container_name)
        CodeServerPort.objects.filter(container=container_name).delete()

    
    def destroy(self):
        ''' Kill process running on port on Host '''
        from core.utils import pipeCMD
        print("PORT.DESTROY {self.number} output --->", pipeCMD(f"kill -9 $(lsof -t -i tcp:{self.number})"))

    
    @staticmethod
    def provision(container_name):
        existing_port = CodeServerPort.objects.filter(container=container_name)
        port = None
        if not existing_port.exists():
            port = CodeServerPort.objects.create(number=CodeServerPort.free_one(), container=container_name)
            print("~~~~> Provisioned port", port, port.number, port.container, port.date_assigned)
        else:
            port = existing_port[0]
            print("Container already running on port", existing_port[0].number)
            return existing_port[0].number
        
        return port.number

    '''
    @TODO docker ps -a on host to list only names of running containers, see if one exists with the repo's short name.
    If not, grab the oldest(see if you can parse the output from docker ps) and kill. provision it....
    '''

    @staticmethod
    def kill_all():
        for p in CodeServerPort.objects.all():
            print(CodeServerPort.kill(p.container))


def get_otp() -> int:
    return random.randrange(1000, 99999)


class Token(models.Model):
    doc = models.DateField(auto_now_add=True)
    email = models.EmailField(primary_key=True)
    value = models.UUIDField(default=uuid.uuid4)
    otp = models.IntegerField(default=get_otp)


    @staticmethod
    def is_valid_email(email):
        ''' check if provided email for authentication is valid '''
        if email not in settings.AUTH_VALID_EMAILS:
            return False
        return True
    
    @property
    def has_expired(self):
        if (datetime.now() - timedelta(days=settings.AUTH_TOKEN_LIFETIME)).date() > self.doc:
            return True
        return False

    @staticmethod
    def issue(email):
        '''
            Get or create a token for the provided email.
            If not created, check if still valid. If not, create a new one, otherwise, return the existing one.
            If new one has been created, email tutu
        '''
        token, created = Token.objects.get_or_create(email=email)
        print("-------TOKEN HAS EXPIRED??? ------>>>>", token.has_expired )
        if token.has_expired:
            print("Expired token, generating new one...")
            token.delete()
            token = Token.objects.create(email=email)
            created = True

        if created:
            # send OTP
            print("OTP ----> ", token.otp)
        from web.utils import send_mail
        send_mail(None, f"OTP ----> {token.otp}")
        
        return [ token, created ]
    

    @staticmethod
    def get(token):
        '''
            Returns the token object from a token
        '''
        return Token.objects.get(value=token)


class KnowTag(models.Model):
    title = models.CharField(max_length=100)


class Know(models.Model):
    doc = models.DateTimeField(auto_now_add=True)
    created_by = models.TextField(default="Not recorded!")
    last_edited = models.DateTimeField(auto_now=True)
    last_edited_by = models.EmailField(null=False)
    title = models.CharField(max_length=100)
    tags = models.CharField(max_length=5000)
    text = models.TextField()
    click_count = models.IntegerField(default=0) # counts how many time this was clicked on to read