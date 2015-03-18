#Google Drive Client

A human python google client

##Dependencies

    sudo pip install google-api-python-client
    sudo pip install httplib2

##How to use

    Eg.
    Cli.py --upload <local_file> <remote_path>
    Upload a signal file
    Cli.py --upload /home/1.zip /aaa/1.zip
    Cli.py --upload /home/1.zip /
    
    Upload a folder
    Cli.py --uploads <local_file> <remote_path>
    Cli.py --uploads /home/php/ /work/php/
    
    List
    Cli.py --ls /home/work/
    Cli.py --ls /
    
    Delete file or folder
    Cli.py --delete /home/work/
    Cli.py --delete /home/work/1.zip
    
    
    This project only include a sample client.You can use Drive.py in yours project.
    Can NOT identified the same name folder in a path.
    
    if you has some folder like this:
    /home/2/
    /home/2/3/
    it possible can not find /home/2/3/