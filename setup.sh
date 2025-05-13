export ZDCROOT=$(realpath -- $(dirname -- ${BASH_SOURCE[0]}))
export ZDCBACKUP="/media/arratialab/CALI/NSRL_test/"

# Function to add a path to an environment variable
add_path_to() {
    local env_var="$1"  
    local path_to_add="$2" 

    # Check if the environment variable is unset or empty
    if [ -z "${!env_var}" ]; then
        export "$env_var=$path_to_add"
    else
        # Check if the path is not already in the environment variable
        if ! [[ "${!env_var}" =~ "$path_to_add" ]]; then
            export "$env_var=$path_to_add:${!env_var}"
        fi
    fi
}

add_path_to PATH ${ZDCROOT}/bin
add_path_to PYTHONPATH ${ZDCROOT}/lib
add_path_to CPLUS_INCLUDE_PATH ${ZDCROOT}/include
add_path_to LD_LIBRARY_PATH ${ZDCROOT}/lib
