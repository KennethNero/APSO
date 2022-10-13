from common import Learner
import subprocess

model = Learner()
obf_strings=[]
for i in range(16):
    obf_strings.append(["0"  if y==i else "1" for y in range(16)])
outputDir="/data/yin-group/models/adv-dnn-ens/workingModel/APSO/results/"
with open("obfuscatorTest.csv",'w') as f:
    f.write("Obfuscator,Confidence\n")
for obf_string in obf_strings:
    cmd = "bash gen_sample.sh " + \
          "/data/yin-group/models/adv-dnn-ens/workingModel/APSO/results/test.apk"+" " + \
          str(obf_string) + " " + \
          outputDir + " " + \
          str(0) + " " + \
          "/data/yin-group/models/adv-dnn-ens/workingModel/APSO/results/test.apk" + " " + \
          "0" + \
          " /usr/local/Obfuscapk/src/" + \
          " /data/yin-group/models/adv-dnn-ens/workingModel/APSO/obfuscapk_tmp " + \
          "test.apk"
    proc = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE)
    
    # Communicate so the output goes to python, and is auto setting the return code
    _, _ = proc.communicate()
    ret_code = proc.returncode
    
    if ret_code == 0:
        # Generate the output name of the new APK
        #APKDir = str(os.path.dirname(newAPKPath))
        newAPKPath = outputDir + "//p" + str(0) + "_i" + str(0) + "_" + "test.apk"
        # print("New APK Path for particle is: \'"+str(newAPKPath)+"\'")
        conf=model.predict([newAPKPath],[1])
        with open("obfuscatorTest.csv",'a') as f:
            f.write("%s,%s\n"%(obf_string,str(conf)))
        from IPython import embed
        embed()
        