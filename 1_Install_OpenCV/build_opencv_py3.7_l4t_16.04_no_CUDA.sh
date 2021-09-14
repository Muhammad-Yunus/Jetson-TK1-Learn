#!/usr/bin/env bash
# 2019 Michael de Gans (https://github.com/mdegans/nano_build_opencv)

set -e

# change default constants here:
readonly PREFIX=/usr  # install prefix, (can be ~/.local for a user install)
readonly DEFAULT_VERSION=4.5.3  # controls the default version (gets reset by the first argument)
readonly CPUS=$(nproc)  # controls the number of jobs

# better board detection. if it has 6 or more cpus, it probably has a ton of ram too
if [[ $CPUS -gt 5 ]]; then
    # something with a ton of ram
    JOBS=$CPUS
else
    JOBS=3  # you can set this to 4 if you have a swap file
    # otherwise a Nano will choke towards the end of the build
fi

cleanup () {
    rm -rf ~/build_opencv
}

setup () {
    cd ~
    if [[ -d "build_opencv" ]] ; then
        echo "It appears an existing build exists in ~/build_opencv"
        #cleanup
    fi
    #mkdir build_opencv
    cd build_opencv
}

git_source () {
    echo "Getting version '$1' of OpenCV"
    git clone --depth 1 --branch "$1" https://github.com/opencv/opencv.git
    git clone --depth 1 --branch "$1" https://github.com/opencv/opencv_contrib.git
}

install_dependencies () {
    # open-cv has a lot of dependencies, but most can be found in the default
    # package repository or should already be installed (eg. CUDA).
    echo "Installing build dependencies."
    sudo apt-get update
    sudo apt-get autoremove
    sudo apt-get install -y \
        build-essential \
        cmake \
        git \
        gfortran \
        libatlas-base-dev \
        libavcodec-dev \
        libavformat-dev \
        libavresample-dev \
        libcanberra-gtk3-module \
        libdc1394-22-dev \
        libeigen3-dev \
        libglew-dev \
        libgstreamer-plugins-base1.0-dev \
        libgstreamer-plugins-good1.0-dev \
        libgstreamer1.0-dev \
        libgtk-3-dev \
        libjpeg-dev \
        libjpeg8-dev \
        libjpeg-turbo8-dev \
        liblapack-dev \
        liblapacke-dev \
        libblas-dev \
        libpng-dev \
        libpostproc-dev \
        libswscale-dev \
        libtbb-dev \
        libtbb2 \
        libtesseract-dev \
        libtiff-dev \
        libv4l-dev \
        libxine2-dev \
        libxvidcore-dev \
        libx264-dev \
        pkg-config \
        qv4l2 \
        v4l-utils \
        v4l2ucp \
        zlib1g-dev \
        gstreamer1.0-tools \
        gstreamer1.0-alsa \
        gstreamer1.0-plugins-base \
        gstreamer1.0-plugins-good \
        gstreamer1.0-plugins-ugly \
        gstreamer1.0-plugins-bad \
        gstreamer1.0-libav
}

configure () {
    local CMAKEFLAGS="
        -D CMAKE_BUILD_TYPE=RELEASE
        -D CMAKE_INSTALL_PREFIX=${PREFIX}
        -D CMAKE_CXX_FLAGS=-Wa,-mimplicit-it=thumb
        -D BUILD_PNG=OFF
        -D BUILD_TIFF=OFF
        -D BUILD_TBB=OFF
        -D BUILD_JPEG=OFF
        -D BUILD_JASPER=OFF
        -D BUILD_ZLIB=OFF
        -D BUILD_EXAMPLES=OFF
        -D BUILD_opencv_apps=OFF
        -D BUILD_opencv_java=OFF
        -D BUILD_opencv_python2=OFF
        -D BUILD_opencv_python3=ON
        -D PYTHON3_EXECUTABLE=/usr/local/bin/python3.7
        -D OPENCV_PYTHON3_INSTALL_PATH=/home/ubuntu/.local/lib/python3.7/site-packages
        -D PYTHON3_NUMPY_INCLUDE_DIRS=/home/ubuntu/.local/lib/python3.7/site-packages/numpy/core/include/
        -D ENABLE_NEON=ON
        -D WITH_OPENCL=ON
        -D WITH_OPENMP=OFF
        -D WITH_FFMPEG=ON
        -D WITH_GSTREAMER=ON
        -D WITH_GSTREAMER_0_10=OFF
        -D WITH_GTK=ON
        -D WITH_VTK=OFF
        -D WITH_TBB=ON
        -D WITH_1394=OFF
        -D WITH_OPENEXR=OFF
        -D WITH_CUDA=OFF
        -D OPENCV_ENABLE_NONFREE=ON
        -D OPENCV_EXTRA_MODULES_PATH=~/build_opencv/opencv_contrib/modules
        -D OPENCV_GENERATE_PKGCONFIG=ON
        -D EIGEN_INCLUDE_PATH=/usr/include/eigen3"

    if [[ "$1" != "test" ]] ; then
        CMAKEFLAGS="
        ${CMAKEFLAGS}
        -D BUILD_PERF_TESTS=OFF
        -D BUILD_TESTS=OFF"
    fi

    echo "cmake flags: ${CMAKEFLAGS}"

    cd opencv
    #mkdir build
    cd build
    cmake ${CMAKEFLAGS} .. 2>&1 | tee -a configure.log
}

main () {

    local VER=${DEFAULT_VERSION}

    # parse arguments
    if [[ "$#" -gt 0 ]] ; then
        VER="$1"  # override the version
    fi

    if [[ "$#" -gt 1 ]] && [[ "$2" == "test" ]] ; then
        DO_TEST=1
    fi

    # prepare for the build:
    setup
    #install_dependencies
    #git_source ${VER}

    if [[ ${DO_TEST} ]] ; then
        configure test
    else
        configure
    fi
    echo "=================================== make start ========================================"
    cd ~/build_opencv/opencv/build/


    # start the build
    echo "USE ${JOBS} JOBS"
    make -j ${JOBS} 2>&1 | tee -a build.log

    if [[ ${DO_TEST} ]] ; then
        make test 2>&1 | tee -a test.log
    fi

    # avoid a sudo make install (and root owned files in ~) if $PREFIX is writable
    if [[ -w ${PREFIX} ]] ; then
        make install 2>&1 | tee -a install.log
    else
        sudo make install 2>&1 | tee -a install.log
    fi

    #cleanup

}

main "$@"

