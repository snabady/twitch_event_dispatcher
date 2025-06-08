import subprocess

def run_xcowsay(image, text, time):

    subprocess.Popen(['xcowsay', 
                        '--monitor',  '0', 
                        text, 
                        '--image=', image, 
                        '--think' , 
                        '--time=' , time,
                        '--at=1080,0'
                        ])
    
def run_mpv():
    pass
