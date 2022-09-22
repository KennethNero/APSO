#! /bin/bash 
# Designed to modify one APK file with a set of obfuscations. The first 
 
# Get the basic inputs. Oh boy. 
in_apk="$1"    # Full path to APK to mod 
in_arr="$2"    # A 16 char string of 0s and 1s 
out_fldr="$3"    # The folder the out file goes into (has a / at the end) 
in_appnd="$4"    # Prefix to be appended to output file 
org_apk="$5"    # The ORIGINAL path to the APK being modded. Used for output generation 
 
# If there are at least 3 underscores AND Particle in the name AND [0] is a case of 0 or 1 
# split at the third underscore 
 
# Set some unwieldy things. 
out_apk="$2_Particle_$4_"$(basename $5) # The out file. Modify as required
# The following indexes in $2 map to the following obfuscations 
#  
# 0 : AdvancedReflection  | # Costly  
# 1 : ArithmeticBranch  |  
# 2 : AssetEncryption  |  
# 3 : CallIndirection  |  
# 4 : ConstStringEncryption |  
# 5 : DebugRemoval  |  
# 6 : FieldRename  |  
# 7 : Goto   |  
# 8 : LibEncryption  |  
# 9 : MethodOverload  |  
# 10: MethodRename  |  
# 11: Nop   |  
# 12: Reflection  | # Costly 
# 13: Reorder   |  
# 14: ResStringEncryption |  
# 15: RandomManifest  | 
 
obf_arr=("AdvancedReflection" "ArithmeticBranch" "AssetEncryption" "CallIndirection" 
"ConstStringEncryption" "DebugRemoval" "FieldRename" "Goto" "LibEncryption" "MethodOverload" 
"MethodRename" "Nop" "Reflection" "Reorder" "ResStringEncryption" "RandomManifest") 
 
# Make sure we're where we need to be 
cd "/usr/local/Obfuscapk/src/obfuscapk/" 
 
# Begin the string construction 
cmd="python3 -m cli.py -w tmp -d $out_fldr$out_apk " 
 
# Loop through the in_arr, append the things 
for (( i=0; i<${#in_arr}; i++ )); do 
    if [ "${in_arr:$i:1}" == "1" ]; then 
        cmd+="-o ${obf_arr[$i]} " 
    fi 
done 
 
# Add the rest of the command to itself 
cmd+="-o Rebuild $in_apk" 
 
# Run it. 
$cmd
