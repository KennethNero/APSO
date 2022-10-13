#! /bin/bash 
# Designed to modify one APK file with a set of obfuscations. The first 
 
# Get the basic inputs. Oh boy. 
in_apk="$1"    # Full path to APK to mod 
in_arr="$2"    # A 16 char string of 0s and 1s 
out_fldr="$3"    # The folder the out file goes into (has a / at the end) 
obf_location="$4" # Absolute path of '....Obfuscapk/src/'
obf_temp_dir="$5"   # Temp directory for use in obfuscapk
apkBasename="$6"  # The thing to name the apk correctly.

# If there are at least 3 underscores AND Particle in the name AND [0] is a c                      ase of 0 or 1
# split at the third underscore

# Set some unwieldy things.
out_apk="${apkBasename}_${in_arr}.apk"
# old_out_apk="$2_Particle_$4_"$(basename $5) # The out file. Modify as required
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
cd "$obf_location"

# Begin the string construction
cmd="python3 -m obfuscapk.cli -w ${obf_temp_dir} -d $out_fldr$out_apk "
 
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
