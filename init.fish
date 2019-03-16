# sd-config initialization hook
#
# You can use the following variables in this file:
# * $package       package name
# * $path          package path
# * $dependencies  package dependencies


set -q __sd_config_path; or set -g __sd_config_path $path
