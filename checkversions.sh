#!/bin/bash
# File: checkversions.sh
# Created: 02/07/2014 by Matt Easton
# Modified: 17/09/2018 by Matt Easton
#
# Prints out the versions of a range of software programs and tools.
# Originally part of pbt-dev.bashrc.
# Options:
#   --paths: show full paths


# Options
## Show paths
[[ "$1" == "--paths" ]] && SHOWPATHS=1 || unset SHOWPATHS

# Colour definitions
source ${SCRIPTS}/definecolours.sh


# Search path for libraries
## Standard paths
LIBRARIES="/usr/lib /usr/lib64 /usr/local/lib /usr/local/lib64"
## Loader search paths
LIBRARIES="${LIBRARIES} $(cat /etc/ld.so.conf.d/*.conf 2>/dev/null | grep -v ^\#)"
## Libraries relative to binary paths (don't do this on WSL)
#LIBRARIES="${LIBRARIES} $(echo $PATH | sed -e 's/:/\n/g' -e 's_/bin_/lib_g')"
#LIBRARIES="${LIBRARIES} $(echo $PATH | sed -e 's/:/\n/g' -e 's_/bin_/lib64_g')"
## Sort and keep unique paths
if [[ "$(uname)" == "Darwin" ]]; then
    LIBRARIES=$(echo -e $LIBRARIES | sort -u)
else
    LIBRARIES=$(echo $LIBRARIES | sed -e 's/ /\n/g' | awk '!x[$0]++')
fi


# Bash version and settings
echo -e "${Cyan} - BASH ${Purple}v${BASH_VERSION%.*}${NC}"
echo -e "${Cyan} - DISPLAY ${Purple}$DISPLAY${NC}"

# Compiling
## GCC
VERSION=$(gcc --version 2>/dev/null | head -n1 | sed -e 's/.*) //')
[[ ${VERSION} && ${SHOWPATHS} ]] && THISPATH="${Yellow} $(which gcc | sed -e 's_/bin/gcc__' -e 's_/root/usr__')${NC}" || THISPATH=""
[[ ! ${VERSION} ]] && VERSION="${BRed}not found${NC}" ||
VERSION="${Purple}v${VERSION}${NC}"
echo -e "${Cyan} - GCC ${VERSION}${THISPATH}${NC}"
## Clang
if [[ "$(uname)" == "Darwin" ]]; then
    VERSION=$(clang --version 2>/dev/null | head -1 | sed -e 's/.*clang-//' -e 's/).*//')
    [[ ${VERSION} && ${SHOWPATHS} ]] && THISPATH="${Yellow} $(which clang | sed -e 's_/bin/clang__')${NC}" || THISPATH=""
    [[ ! ${VERSION} ]] && VERSION="${BRed}not found${NC}" || VERSION="${Purple}v${VERSION}${NC}"
    echo -e "${Cyan} - Clang ${VERSION}${THISPATH}${NC}"
fi
## CMake
VERSION=$(cmake --version 2>/dev/null | head -n1 | cut -c15-)
[[ ${VERSION} && ${SHOWPATHS} ]] && THISPATH="${Yellow} $(which cmake | grep -v "alias" | sed -e 's/\t//' -e 's_/bin/cmake__')${NC}" || THISPATH=""
[[ ! ${VERSION} ]] && VERSION="${BRed}not found${NC}" || VERSION="${Purple}v${VERSION}${NC}"
echo -e "${Cyan} - CMake ${VERSION}${THISPATH}${NC}"
## OpenMPI
VERSION=$(mpirun --version 2>/dev/null | head -n1 | sed -e 's/.*) //')
[[ ${VERSION} && ${SHOWPATHS} ]] && THISPATH="${Yellow} $(which mpirun | grep -v "alias" | sed -e 's_/bin/mpirun__')${NC}" || THISPATH=""
[[ ! ${VERSION} ]] && VERSION="${BRed}not found${NC}" || VERSION="${Purple}v${VERSION}${NC}"
echo -e "${Cyan} - OpenMPI ${VERSION}${THISPATH}${NC}"

# Graphics
## OpenGL
VERSION=$(glxinfo 2>/dev/null | grep -B0 -A0 -m1 --colour=never "OpenGL version" | sed -e 's/.*string: //' -e 's/ (.*//' -e 's/ .*$//')
[[ ${VERSION} && ${SHOWPATHS} ]] && THISPATH="${Yellow} $(which glxinfo | sed -e 's_/bin/glxinfo__')${NC}" || THISPATH=""
[[ ! ${VERSION} ]] && VERSION="${BRed}not found${NC}" || VERSION="${Purple}v${VERSION}${NC}"
echo -e "${Cyan} - OpenGL ${VERSION}${THISPATH}${NC}"
## Qt
if [[ "$(uname)" == "Darwin" ]]; then
    VERSION=$(brew list --versions qt | sed -e 's/qt //')
    [[ ${VERSION} && ${SHOWPATHS} ]] && THISPATH="${Yellow} $(find ${LIBRARIES} -name QtCore.framework 2>/dev/null | head -1 | sed -e "s_/lib/QtCore.framework__")${NC}" || THISPATH=""
else
    VERSION=$(find ${LIBRARIES} -name libQt*Core.so.* 2>/dev/null | sed -e 's/.*libQt.*Core.so.//' | sort | tail    -1)
    [[ ${VERSION} && ${SHOWPATHS} ]] && THISPATH="${Yellow} $(find ${LIBRARIES} -name libQt*Core.so.${VERSION} 2>/dev/null | head -1 | sed -e "s_/lib.*/libQt.*Core.so.${VERSION}__")${NC}" || THISPATH=""
fi
[[ ! ${VERSION} ]] && VERSION="${BRed}not found${NC}" || VERSION="${Purple}v${VERSION}${NC}"
echo -e "${Cyan} - Qt ${VERSION}${THISPATH}${NC}"
VERSION=$(qmake --version 2>&1 | grep -B0 -A0 -m1 --colour=never version | sed -e 's/.*version: //' -e 's/.*version //')
[[ ${VERSION} && ${SHOWPATHS} ]] && THISPATH="${Yellow} $(which qmake | sed -e 's_/bin/qmake__')${NC}" || THISPATH=""
[[ ! ${VERSION} ]] && VERSION="${BRed}not found${NC}" || VERSION="${Purple}v${VERSION}${NC}"
echo -e "${Cyan}   - qmake ${VERSION}${THISPATH}${NC}"

# Physics tools
## ROOT
if [ -r "/opt/root/bin/thisroot.sh" ] ; then
    source "/opt/root/bin/thisroot.sh"
fi
VERSION=$(root-config --version 2>/dev/null)
[[ ${VERSION} && ${SHOWPATHS} ]] && THISPATH="${Yellow} $(which root-config | sed -e 's_/bin/root-config__')${NC}" || THISPATH=""
[[ ! ${VERSION} ]] && VERSION="${BRed}not found${NC}" || VERSION="${Purple}v${VERSION}${NC}"
echo -e "${Cyan} - ROOT ${VERSION}${THISPATH}${NC}"
## CLHEP
VERSION=$(clhep-config --version 2>/dev/null | sed -e 's/CLHEP //')
[[ ${VERSION} && ${SHOWPATHS} ]] && THISPATH="${Yellow} $(which clhep-config | sed -e 's_/bin/clhep-config__')${NC}" || THISPATH=""
[[ ! ${VERSION} ]] && VERSION="${BRed}not found${NC}" || VERSION="${Purple}v${VERSION}${NC}"
echo -e "${Cyan} - CLHEP ${VERSION}${THISPATH}${NC}"
## Geant4 and related tools
### Geant4 itself
if [ -r "$(which geant4-config | sed -e 's_/geant4-config__')/geant4.sh" ] ; then
    source "$(which geant4-config | sed -e 's_/geant4-config__')/geant4.sh"
elif [ -r "/usr/local/bin/geant4.sh" ] ; then
    source "/usr/local/bin/geant4.sh"
fi
VERSION=$(geant4-config --version 2>/dev/null)
[[ ${VERSION} && ${SHOWPATHS} ]] && THISPATH="${Yellow} $(which geant4-config | sed -e 's_/bin/geant4-config__')${NC}" || THISPATH=""
[[ ! ${VERSION} ]] && VERSION="${BRed}not found${NC}" || VERSION="${Purple}v${VERSION}${NC}"
echo -e "${Cyan} - GEANT4 ${VERSION}${THISPATH}${NC}"
### Xerces-C++
VERSION=$(find ${LIBRARIES} -name libxerces-c-* 2>/dev/null | sed -e 's/.*libxerces-c-//' -e 's/.dylib//' -e 's/.so//' | sort | tail -1)
[[ ${VERSION} && ${SHOWPATHS} ]] && THISPATH="${Yellow} $(find ${LIBRARIES} -name libxerces-c-${VERSION}.* 2>/dev/null | head -1 | sed -e "s_/lib.*/libxerces-c-${VERSION}.*__")${NC}" || THISPATH=""
[[ ! ${VERSION} ]] && VERSION="${BRed}not found${NC}" || VERSION="${Purple}v${VERSION}${NC}"
echo -e "${Cyan}   - Xerces-C++ ${VERSION}${THISPATH}${NC}"
### Motif
if [[ "$(uname)" == "Darwin" ]]; then
    VERSION=$(motif-config --version 2>/dev/null | sed -e 's/.*if //')
    [[ ${VERSION} && ${SHOWPATHS} ]] && THISPATH="${Yellow} $(which motif-config | sed -e 's_/bin/motif-config__')${NC}" || THISPATH=""
else
    VERSION=$(find ${LIBRARIES} -name libXm.so.* 2>/dev/null | sed -e 's/.*libXm.so.//' | sort | tail -1)
    [[ ${VERSION} && ${SHOWPATHS} ]] && THISPATH="${Yellow} $(find ${LIBRARIES} -name libXm.so.${VERSION} 2>/dev/null | head -1 | sed -e "s_/lib.*/libXm.so.${VERSION}__")${NC}" || THISPATH=""
fi
[[ ! ${VERSION} ]] && VERSION="${BRed}not found${NC}" || VERSION="${Purple}v${VERSION}${NC}"
echo -e "${Cyan}   - Motif ${VERSION}${THISPATH}${NC}"
### Coin3D
VERSION=$(coin-config --version 2>/dev/null)
[[ ${VERSION} && ${SHOWPATHS} ]] && THISPATH="${Yellow} $(which coin-config | sed -e 's_/bin/coin-config__')${NC}" || THISPATH=""
[[ ! ${VERSION} ]] && VERSION="${BRed}not found${NC}" || VERSION="${Purple}v${VERSION}${NC}"
echo -e "${Cyan}   - Coin3D ${VERSION}${THISPATH}${NC}"
VERSION=$(soqt-config --version 2>/dev/null)
[[ ${VERSION} && ${SHOWPATHS} ]] && THISPATH="${Yellow} $(which soqt-config | sed -e 's_/bin/soqt-config__')${NC}" || THISPATH=""
[[ ! ${VERSION} ]] && VERSION="${BRed}not found${NC}" || VERSION="${Purple}v${VERSION}${NC}"
echo -e "${Cyan}     - SoQt library ${VERSION}${THISPATH}${NC}"
VERSION=$(soxt-config --version 2>/dev/null)
[[ ${VERSION} && ${SHOWPATHS} ]] && THISPATH="${Yellow} $(which soxt-config | sed -e 's_/bin/soxt-config__')${NC}" || THISPATH=""
[[ ! ${VERSION} ]] && VERSION="${BRed}not found${NC}" || VERSION="${Purple}v${VERSION}${NC}"
echo -e "${Cyan}     - SoXt library ${VERSION}${THISPATH}${NC}"
### DAWN
VERSION=$(dawn -h 2>&1 | grep -B0 -A0 -m1 --colour=never "ver " | sed -e 's/.*ver //' -e 's/ (.*//')
[[ ${VERSION} && ${SHOWPATHS} ]] && THISPATH="${Yellow} $(which dawn | sed -e 's_/bin/dawn__')${NC}" || THISPATH=""
[[ ! ${VERSION} ]] && VERSION="${BRed}not found${NC}" || VERSION="${Purple}v${VERSION}${NC}"
echo -e "${Cyan}   - DAWN ${VERSION}${THISPATH}${NC}"
### HepRApp [hard-coded as incorrect version is reported by the Java jar-file manifest, and unlikely to change version]
[[ $(which HepRApp.jar 2>/dev/null) ]] && VERSION="${Purple}v3.15.4${NC}" || VERSION="${BRed}not found${NC}"
[[ ${SHOWPATHS} ]] && THISPATH="${Yellow} $(which HepRApp.jar 2>/dev/null | sed -e 's_/bin/HepRApp.jar__')${NC}" || THISPATH=""
echo -e "${Cyan}   - HepRApp ${VERSION}${THISPATH}${NC}"
### JAS3 for WIRED4
VERSION=$(ls -l $(which -a jas3 2>/dev/null) 2>/dev/null | grep -B0 -A0 -m1 --colour=never "jas-assembly" | sed -e 's/.*jas-assembly-//' -e 's_/bin/jas3__')
[[ ${VERSION} && ${SHOWPATHS} ]] && THISPATH="${Yellow} $(which jas3 | sed -e 's_/bin/jas3__')${NC}" || THISPATH=""
[[ ! ${VERSION} ]] && VERSION="${BRed}not found${NC}" || VERSION="${Purple}v${VERSION}${NC}"
echo -e "${Cyan}   - JAS3 for WIRED4 ${VERSION}${THISPATH}${NC}"
### gMocren - not installed at PKU
#VERSION=$(ls -l $(which -a gMocren4 2>/dev/null) 2>/dev/null | grep -B0 -A0 -m1 --colour=never "gMocren" | sed -e 's/.*gmocren-//' -e 's/.*gMocren-//' -e 's_/bin/gMocren4__')
#[[ ${VERSION} && ${SHOWPATHS} ]] && THISPATH="${Yellow} $(which gMocren4 | sed -e 's_/bin/gMocren4__')${NC}" || THISPATH=""
#[[ ! ${VERSION} ]] && VERSION="${BRed}not found${NC}" || VERSION="${Purple}v${VERSION}${NC}"
#echo -e "${Cyan}    - gMocren ${VERSION}${THISPATH}${NC}"
## BDSIM
if [ -r "${SCRIPTS}/bdsim.sh" ] ; then
    source "${SCRIPTS}/bdsim.sh"
fi
VERSION=$(bdsim --version 2>/dev/null | head -n1 | cut -c 17-)
[[ ${VERSION} && ${SHOWPATHS} ]] && THISPATH="${Yellow} $(which bdsim | sed -e 's_/bin/bdsim__')${NC}" || THISPATH=""
[[ ! ${VERSION} ]] && VERSION="${BRed}not found${NC}" || VERSION="${Purple}v${VERSION}${NC}"
echo -e "${Cyan} - BDSIM ${VERSION}${THISPATH}${NC}"
