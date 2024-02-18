############################
# FFMPEG
############################
FROM archlinux as ffmpeg-arch
RUN --mount=type=cache,sharing=locked,target=/var/cache/pacman \
  pacman -Syu --noconfirm --needed base base-devel cuda git
ENV NVIDIA_VISIBLE_DEVICES all
ENV NVIDIA_DRIVER_CAPABILITIES compute,utility
ARG user=makepkg
RUN useradd --system --create-home $user && \
  echo "$user ALL=(ALL:ALL) NOPASSWD:ALL" >/etc/sudoers.d/$user
USER $user
WORKDIR /home/$user
RUN git clone https://aur.archlinux.org/yay.git && \
  cd yay && \
  makepkg -sri --needed --noconfirm && \
  cd && \
  rm -rf .cache yay

RUN yay -Syu rust tcl nasm cmake jq libtool wget fribidi fontconfig libsoxr meson pod2man nvidia-utils base-devel --noconfirm --ask 4
USER root

RUN mkdir -p "/home/makepkg/python311"
RUN wget https://github.com/python/cpython/archive/refs/tags/v3.11.3.tar.gz && tar xf v3.11.3.tar.gz && cd cpython-3.11.3 && \
  mkdir debug && cd debug && ../configure --enable-optimizations --disable-shared --prefix="/home/makepkg/python311" && make -j$(nproc) && make install && \
  /home/makepkg/python311/bin/python3.11 -m ensurepip --upgrade
RUN cp /home/makepkg/python311/bin/python3.11 /usr/bin/python
ENV PYTHONPATH /home/makepkg/python311/bin/
ENV PATH "/home/makepkg/python311/bin/:$PATH"

RUN pip3 install cython meson

ENV PATH "$PATH:/opt/cuda/bin/nvcc"
ENV PATH "$PATH:/opt/cuda/bin"
ENV LD_LIBRARY_PATH "/opt/cuda/lib64"

# -O3 makes sure we compile with optimization. setting CFLAGS/CXXFLAGS seems to override
# default automake cflags.
# -static-libgcc is needed to make gcc not include gcc_s as "as-needed" shared library which
# cmake will include as a implicit library.
# other options to get hardened build (same as ffmpeg hardened)
ARG CFLAGS="-O3 -static-libgcc -fno-strict-overflow -fstack-protector-all -fPIE"
ARG CXXFLAGS="-O3 -static-libgcc -fno-strict-overflow -fstack-protector-all -fPIE"
ARG LDFLAGS="-Wl,-z,relro,-z,now"

# master is broken https://github.com/sekrit-twc/zimg/issues/181
# No rule to make target 'graphengine/graphengine/cpuinfo.cpp', needed by 'graphengine/graphengine/libzimg_internal_la-cpuinfo.lo'.  Stop.
RUN git clone https://github.com/sekrit-twc/zimg --depth 1 --recurse-submodules --shallow-submodules && cd zimg && \
  ./autogen.sh && CFLAGS=-fPIC CXXFLAGS=-fPIC ./configure --enable-static --disable-shared && make -j$(nproc) && make install

ENV PATH /usr/local/bin:$PATH
RUN wget https://github.com/vapoursynth/vapoursynth/archive/refs/tags/R65.tar.gz && \
  tar -zxvf R65.tar.gz && cd vapoursynth-R65 && ./autogen.sh && \
  PKG_CONFIG_PATH="/usr/lib/pkgconfig:/usr/local/lib/pkgconfig" ./configure --enable-static --disable-shared && \
  make && make install && cd .. && ldconfig

RUN git clone https://github.com/gypified/libmp3lame && cd libmp3lame && ./configure --enable-static --enable-nasm --disable-shared && make -j$(nproc) install

RUN git clone https://github.com/mstorsjo/fdk-aac/ && \
  cd fdk-aac && ./autogen.sh && ./configure --enable-static --disable-shared && make -j$(nproc) install

RUN git clone https://github.com/xiph/ogg && cd ogg && ./autogen.sh && ./configure --enable-static --disable-shared && make -j$(nproc) install

RUN git clone https://github.com/xiph/vorbis && cd vorbis && ./autogen.sh && ./configure --enable-static --disable-shared && make -j$(nproc) install

RUN git clone https://github.com/xiph/opus && cd opus && ./autogen.sh && ./configure --enable-static --disable-shared && make -j$(nproc) install

RUN git clone https://github.com/xiph/theora && cd theora && ./autogen.sh && ./configure --disable-examples --enable-static --disable-shared && make -j$(nproc) install

RUN git clone https://github.com/webmproject/libvpx/ && \
  cd libvpx && ./configure --enable-static --enable-vp9-highbitdepth --disable-shared --disable-unit-tests --disable-examples && \
  make -j$(nproc) install

RUN git clone https://code.videolan.org/videolan/x264.git && \
  cd x264 && ./configure --enable-pic --enable-static && make -j$(nproc) install

# -w-macro-params-legacy to not log lots of asm warnings
# https://bitbucket.org/multicoreware/x265_git/issues/559/warnings-when-assembling-with-nasm-215
RUN git clone https://bitbucket.org/multicoreware/x265_git/ && cd x265_git/build/linux && \
  cmake -G "Unix Makefiles" -DENABLE_SHARED=OFF -D HIGH_BIT_DEPTH:BOOL=ON -DENABLE_AGGRESSIVE_CHECKS=ON ../../source -DCMAKE_ASM_NASM_FLAGS=-w-macro-params-legacy && \
  make -j$(nproc) install

RUN git clone https://github.com/webmproject/libwebp/ && \
  cd libwebp && ./autogen.sh && ./configure --enable-static --disable-shared && make -j$(nproc) install

RUN git clone https://github.com/xiph/speex/ && \
  cd speex && ./autogen.sh && ./configure --enable-static --disable-shared && make -j$(nproc) install

RUN git clone --depth 1 https://aomedia.googlesource.com/aom && \
  cd aom && \
  mkdir build_tmp && cd build_tmp && cmake -DBUILD_SHARED_LIBS=0 -DENABLE_TESTS=0 -DENABLE_NASM=on -DCMAKE_INSTALL_LIBDIR=lib .. && make -j$(nproc) install

RUN git clone https://github.com/georgmartius/vid.stab/ && \
  cd vid.stab && cmake -DBUILD_SHARED_LIBS=OFF . && make -j$(nproc) install

RUN git clone https://github.com/ultravideo/kvazaar/ && \
  cd kvazaar && ./autogen.sh && ./configure --enable-static --disable-shared && make -j$(nproc) install

RUN git clone https://github.com/libass/libass/ && \
  cd libass && ./autogen.sh && ./configure --enable-static --disable-shared && make -j$(nproc) && make install

RUN git clone https://github.com/uclouvain/openjpeg/ && \
  cd openjpeg && cmake -G "Unix Makefiles" -DBUILD_SHARED_LIBS=OFF && make -j$(nproc) install

RUN git clone https://code.videolan.org/videolan/dav1d/ && \
  cd dav1d && meson build --buildtype release -Ddefault_library=static && ninja -C build install

# add extra CFLAGS that are not enabled by -O3
# http://websvn.xvid.org/cvs/viewvc.cgi/trunk/xvidcore/build/generic/configure.in?revision=2146&view=markup
ARG XVID_VERSION=1.3.7
ARG XVID_URL="https://downloads.xvid.com/downloads/xvidcore-$XVID_VERSION.tar.gz"
ARG XVID_SHA256=abbdcbd39555691dd1c9b4d08f0a031376a3b211652c0d8b3b8aa9be1303ce2d
RUN wget -O libxvid.tar.gz "$XVID_URL" && \
  echo "$XVID_SHA256  libxvid.tar.gz" | sha256sum --status -c - && \
  tar xf libxvid.tar.gz && \
  cd xvidcore/build/generic && \
  CFLAGS="$CLFAGS -fstrength-reduce -ffast-math" \
    ./configure && make -j$(nproc) && make install

RUN rm -rf rav1e && \
    git clone https://github.com/xiph/rav1e/ && \
    cd rav1e && \
    cargo install cargo-c && \
    cargo cinstall --release --library-type=staticlib --crt-static && \
    sed -i 's/-lgcc_s//' /usr/local/lib/pkgconfig/rav1e.pc

RUN git clone https://github.com/Haivision/srt/ && \
  cd srt && ./configure --enable-shared=0 --cmake-install-libdir=lib --cmake-install-includedir=include --cmake-install-bindir=bin && \
  make -j$(nproc) && make install

RUN git clone https://gitlab.com/AOMediaCodec/SVT-AV1/ && \
  cd SVT-AV1 && \
  sed -i 's/picture_copy(/svt_av1_picture_copy(/g' \
    Source/Lib/Common/Codec/EbPictureOperators.c \
    Source/Lib/Common/Codec/EbPictureOperators.h \
    Source/Lib/Encoder/Codec/EbFullLoop.c \
    Source/Lib/Encoder/Codec/EbProductCodingLoop.c && \
  cd Build && \
  cmake .. -G"Unix Makefiles" -DCMAKE_INSTALL_LIBDIR=lib -DBUILD_SHARED_LIBS=OFF -DCMAKE_BUILD_TYPE=Release && \
  make -j$(nproc) install

RUN git clone https://github.com/pkuvcl/davs2/ && \
  cd davs2/build/linux && ./configure --disable-asm --enable-pic && \
  make -j$(nproc) install

RUN git clone https://github.com/pkuvcl/xavs2/ && \
  cd xavs2/build/linux && ./configure --disable-asm --enable-pic && \
  make -j$(nproc) install

RUN git clone https://github.com/Netflix/vmaf/ && \
  cd vmaf/libvmaf && meson build --buildtype release -Ddefault_library=static && ninja -vC build install

RUN git clone https://github.com/cisco/openh264 && \
  cd openh264 && meson build --buildtype release -Ddefault_library=static && ninja -C build install

RUN git clone https://github.com/FFmpeg/nv-codec-headers && cd nv-codec-headers && make -j$(nproc) && make install

# https://github.com/shadowsocks/shadowsocks-libev/issues/623
RUN mkdir -p "/home/makepkg/ssl"
RUN git clone git://git.openssl.org/openssl.git && cd openssl && LIBS="-ldl -lz" LDFLAGS="-Wl,-static -static -static-libgcc -s" \
  ./config no-shared -static --prefix="/home/makepkg/ssl" --openssldir="/home/makepkg/ssl" && \
  sed -i 's/^LDFLAGS = /LDFLAGS = -all-static -s/g' Makefile && make -j$(nproc) && make install_sw && make install

# https://stackoverflow.com/questions/18185618/how-to-use-static-linking-with-openssl-in-c-c
RUN git clone https://github.com/FFmpeg/FFmpeg
ENV NVCC_PREPEND_FLAGS='-ccbin /usr/bin/g++-12'
RUN cd FFmpeg && \
  PKG_CONFIG_PATH=/usr/local/lib/pkgconfig/:/home/makepkg/ssl/lib64/pkgconfig/ ./configure \
    --extra-cflags="-fopenmp -lcrypto -lz -ldl -static-libgcc -I/opt/cuda/include" \
    --extra-cxxflags="-fopenmp -lcrypto -lz -ldl -static-libgcc" \
    --extra-ldflags="-fopenmp -lcrypto -lz -ldl -static-libgcc -L/opt/cuda/lib64" \
    --extra-libs="-lstdc++ -lcrypto -lz -ldl -static-libgcc" \
    --pkg-config-flags=--static \
    --toolchain=hardened \
    --disable-debug \
    --disable-shared \
    --disable-doc \
    --disable-ffplay \
    --enable-static \
    --enable-gpl \
    --enable-gray \
    --enable-nonfree \
    --enable-openssl \
    --enable-iconv \
    --enable-libxml2 \
    --enable-libmp3lame \
    --enable-libfdk-aac \
    --enable-libvorbis \
    --enable-libopus \
    --enable-libtheora \
    --enable-libvpx \
    --enable-libx264 \
    --enable-libx265 \
    --enable-libwebp \
    --enable-libspeex \
    --enable-libaom \
    --enable-libvidstab \
    --enable-libkvazaar \
    --enable-libfreetype \
    --enable-fontconfig \
    --enable-libfribidi \
    --enable-libass \
    --enable-libsoxr \
    --enable-libopenjpeg \
    --enable-libdav1d \
    --enable-librav1e \
    --enable-libsrt \
    --enable-libsvtav1 \
    --enable-libdavs2 \
    --enable-libxavs2 \
    --enable-libvmaf \
    --enable-cuda-nvcc \
    --enable-vapoursynth \
    #--enable-hardcoded-tables \
    --enable-libopenh264 \
    --enable-optimizations \
    --enable-cuda-llvm \
    --enable-nvdec \
    --enable-nvenc \
    --enable-cuvid \
    --enable-cuda \
    --enable-pthreads \
    --enable-runtime-cpudetect \
    --enable-lto && \
    make -j$(nproc)
  
############################
# MMCV
############################
FROM nvidia/cuda:12.1.1-devel-ubuntu22.04 as mmcv-ubuntu

ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get -y update && apt-get install -y \
  curl \
  make \
  gcc \
  wget \
  libssl-dev \
  libffi-dev \
  libopenblas-dev \
  python3.11 \
  python3.11-dev \
  python3.11-venv \
  python3-pip \
  git && \
  apt-get autoclean -y && \
  apt-get autoremove -y && \
  apt-get clean -y

RUN python3.11 -m pip install --upgrade pip
RUN python3.11 -m pip install torch torchvision torchaudio
RUN python3.11 -m pip install ninja
# own fork due to required c++17
# error C++17 or later compatible compiler is required to use ATen.
RUN git clone https://github.com/styler00dollar/mmcv --recursive && cd mmcv && MMCV_WITH_OPS=1 python3.11 setup.py build_ext && \
  MMCV_WITH_OPS=1 MAKEFLAGS="-j$(nproc)" python3.11 setup.py bdist_wheel

############################
# cupy
############################

FROM nvidia/cuda:12.1.1-devel-ubuntu22.04 as cupy-ubuntu

ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get -y update && apt-get install -y \
  curl \
  make \
  gcc \
  wget \
  libssl-dev \
  libffi-dev \
  libopenblas-dev \
  python3.11 \
  python3.11-dev \
  python3.11-venv \
  python3-pip \
  git && \
  apt-get autoclean -y && \
  apt-get autoremove -y && \
  apt-get clean -y

RUN python3.11 -m pip install --upgrade pip
RUN python3.11 -m pip install torch torchvision torchaudio
RUN git clone https://github.com/cupy/cupy --recursive && cd cupy && git submodule update --init && python3.11 -m pip install . && \
  MAKEFLAGS="-j$(nproc)" python3.11 setup.py bdist_wheel

############################
# bestsource / lsmash / ffms2
# todo: check if CFLAGS=-fPIC CXXFLAGS=-fPIC LDFLAGS="-Wl,-Bsymbolic" --extra-ldflags="-static" is required
############################
FROM ubuntu:22.04 as bestsource-lsmash-ffms2-vs

ARG DEBIAN_FRONTEND=noninteractive
WORKDIR workspace

RUN apt update -y
RUN apt install autoconf libtool nasm ninja-build yasm python3.11 python3.11-venv python3.11-dev python3-pip wget git pkg-config python-is-python3 -y
RUN apt --fix-broken install
RUN pip install meson ninja cython

# install g++13
RUN apt install build-essential manpages-dev software-properties-common -y
RUN add-apt-repository ppa:ubuntu-toolchain-r/test -y
RUN apt update -y && apt install gcc-13 g++-13 -y
RUN update-alternatives --install /usr/bin/gcc gcc /usr/bin/gcc-13 13
RUN update-alternatives --install /usr/bin/g++ g++ /usr/bin/g++-13 13

# zimg
# setting pkg version manually since otherwise 'Version' field value '-1': version number is empty
RUN apt-get install checkinstall -y
RUN git clone https://github.com/sekrit-twc/zimg --recursive && cd zimg && \
  ./autogen.sh && CFLAGS=-fPIC CXXFLAGS=-fPIC ./configure --enable-static --disable-shared && make -j$(nproc) && checkinstall -y -pkgversion=0.0 && \
  apt install /workspace/zimg/zimg_0.0-1_amd64.deb -y

# vapoursynth
RUN wget https://github.com/vapoursynth/vapoursynth/archive/refs/tags/R65.tar.gz && \
  tar -zxvf R65.tar.gz && mv vapoursynth-R65 vapoursynth && cd vapoursynth && \
  ./autogen.sh && CFLAGS=-fPIC CXXFLAGS=-fPIC ./configure --enable-static --disable-shared && make -j$(nproc) && make install && ldconfig

# dav1d
RUN git clone https://code.videolan.org/videolan/dav1d/ && \
  cd dav1d && meson build --buildtype release -Ddefault_library=static && ninja -C build install

# ffmpeg
RUN apt remove ffmpeg -y
RUN git clone https://git.ffmpeg.org/ffmpeg.git --depth 1 && cd ffmpeg && \
  CFLAGS=-fPIC ./configure --disable-shared --enable-static --enable-gpl --enable-version3 --disable-programs --disable-doc --disable-avdevice --disable-swresample --disable-postproc --disable-avfilter --disable-encoders --disable-muxers --disable-debug --enable-pic --extra-ldflags="-static" --extra-cflags="-march=native" && \
  make -j$(nproc) && make install -j$(nproc)

# jansson
RUN git clone https://github.com/akheron/jansson && cd jansson && autoreconf -fi && CFLAGS=-fPIC ./configure --disable-shared --enable-static && \
  make -j$(nproc) && make install

# Vulkan-Headers
Run apt install cmake -y
RUN git clone https://github.com/KhronosGroup/Vulkan-Headers.git && cd Vulkan-Headers/ && cmake -S . -DBUILD_SHARED_LIBS=OFF -B build/ && cmake --install build

# nv-codec-headers
RUN git clone https://github.com/FFmpeg/nv-codec-headers && cd nv-codec-headers && make -j$(nproc) && make install

# bzip2
RUN git clone https://github.com/libarchive/bzip2 && cd bzip2 && \
  mkdir build && cd build && cmake .. -DBUILD_SHARED_LIBS=OFF && make -j$(nproc) && make install

# bestsource
RUN apt-get install -y && git clone https://github.com/vapoursynth/bestsource && cd bestsource && git clone https://github.com/sekrit-twc/libp2p.git --depth 1 && \
  CFLAGS=-fPIC meson setup -Dlink_static=true build && CFLAGS=-fPIC ninja -C build && ninja -C build install

# ffmpeg (HomeOfAviSynthPlusEvolution version with sws)
# official ffmpeg does not compile
# fatal error: libswresample/swresample.h: No such file or directory
RUN apt remove ffmpeg -y
RUN rm -rf FFmpeg
RUN git clone https://github.com/HomeOfAviSynthPlusEvolution/FFmpeg --depth 1 
RUN cd FFmpeg && \
  LDFLAGS="-Wl,-Bsymbolic" CFLAGS=-fPIC ./configure --disable-shared --enable-static --enable-gpl --enable-version3 --disable-programs --disable-doc --disable-avdevice --disable-postproc --disable-avfilter --disable-encoders --disable-muxers --disable-debug --enable-pic --extra-ldflags="-Wl,-Bsymbolic" --extra-cflags="-march=native" && \
  make -j$(nproc) && make install -j$(nproc)

# lsmash
RUN git clone https://github.com/l-smash/l-smash && cd l-smash && CFLAGS=-fPIC CXXFLAGS=-fPIC LDFLAGS="-Wl,-Bsymbolic" ./configure --enable-shared --extra-ldflags="-Wl,-Bsymbolic"  && \
  make -j$(nproc) && make install
RUN git clone https://github.com/HomeOfAviSynthPlusEvolution/L-SMASH-Works && cd L-SMASH-Works && \
   cd VapourSynth/ && CFLAGS=-fPIC CXXFLAGS=-fPIC LDFLAGS="-Wl,-Bsymbolic" meson build && CFLAGS=-fPIC CXXFLAGS=-fPIC LDFLAGS="-Wl,-Bsymbolic" ninja -C build && ninja -C build install 

# ffms2
RUN apt install autoconf -y
RUN git clone https://github.com/FFMS/ffms2 && cd ffms2 && ./autogen.sh && CFLAGS=-fPIC CXXFLAGS=-fPIC LDFLAGS="-Wl,-Bsymbolic" ./configure --enable-shared && make -j$(nproc) && make install

############################
# OpenCV
############################
FROM nvidia/cuda:12.1.1-runtime-ubuntu22.04 as opencv-ubuntu
ARG DEBIAN_FRONTEND=noninteractive
ENV NVIDIA_VISIBLE_DEVICES all
ENV NVIDIA_DRIVER_CAPABILITIES all

RUN apt-get update && apt-get upgrade -y &&\
    apt-get install -y \
        build-essential \
        cmake \
        git \
        wget \
        unzip \
        yasm \
        pkg-config \
        libswscale-dev \
        libtbb2 \
        libtbb-dev \
        libjpeg-dev \
        libpng-dev \
        libtiff-dev \
        libavformat-dev \
        libpq-dev \
        libxine2-dev \
        libglew-dev \
        libtiff5-dev \
        zlib1g-dev \
        libjpeg-dev \
        libavcodec-dev \
        libavformat-dev \
        libavutil-dev \
        libpostproc-dev \
        libswscale-dev \
        libeigen3-dev \
        libtbb-dev \
        libgtk2.0-dev \
        pkg-config \
        ## Python
        python3.11 \
        python3.11-dev \
        python3.11-venv \
        python3-pip \
    && rm -rf /var/lib/apt/lists/*

# OpenCV (pip install . fails currently, building wheel instead)
RUN python3.11 -m pip install --upgrade pip setuptools wheel && python3.11 -m pip install scikit-build -U && \
  git clone --recursive https://github.com/opencv/opencv-python && \
  cd opencv-python && \
  # git checkout 45e535e34d3dc21cd4b798267bfa94ee7c61e11c && \
  git submodule update --init --recursive && \
  # git submodule update --remote --merge && \
  CMAKE_ARGS="-DOPENCV_EXTRA_MODULES_PATH=/opencv-python/opencv_contrib/modules \
  -DBUILD_opencv_cudacodec=OFF -DBUILD_opencv_cudaoptflow=OFF \ 
  -D ENABLE_FAST_MATH=1 \
  -D CUDA_FAST_MATH=1 \
  -D WITH_CUBLAS=1 \
  -D BUILD_TIFF=ON \
  -D BUILD_opencv_java=OFF \
  -D WITH_CUDA=ON \
  -D WITH_OPENGL=ON \
  -D WITH_OPENCL=ON \
  -D WITH_IPP=ON \
  -D WITH_TBB=ON \
  -D WITH_EIGEN=ON \
  -D WITH_V4L=OFF  \
  -D BUILD_TESTS=OFF \
  -D BUILD_PERF_TESTS=OFF \
  -D OPENCV_FFMPEG_USE_FIND_PACKAGE=OFF \
  -D BUILD_SHARED_LIBS=OFF \
  -D CUDA_ARCH_BIN=7.5,8.0,8.6,8.9,7.5+PTX,8.0+PTX,8.6+PTX,8.9+PTX \
  -D CMAKE_BUILD_TYPE=RELEASE" \
  ENABLE_ROLLING=1 ENABLE_CONTRIB=1 MAKEFLAGS="-j$(nproc)" \
  python3.11 -m pip wheel . --verbose


############################
# TensorRT + ORT
############################
FROM nvidia/cuda:12.1.1-devel-ubuntu22.04 as TensorRT-ubuntu

ARG DEBIAN_FRONTEND=noninteractive

# install python
# https://stackoverflow.com/questions/75159821/installing-python-3-11-1-on-a-docker-container
# https://stackoverflow.com/questions/45954528/pip-is-configured-with-locations-that-require-tls-ssl-however-the-ssl-module-in
# /usr/local/lib/libpython3.11.a(longobject.o): relocation R_X86_64_PC32 against symbol `_Py_NotImplementedStruct' can not be used when making a shared object; recompile with -fPIC
# todo: test CFLAGS="-fPIC -march=native"
RUN apt update -y && apt install liblzma-dev libbz2-dev ca-certificates openssl libssl-dev libncurses5-dev libsqlite3-dev libreadline-dev libtk8.6 libgdm-dev \
  libdb4o-cil-dev libpcap-dev software-properties-common wget zlib1g-dev -y && \
  wget https://www.python.org/ftp/python/3.11.3/Python-3.11.3.tar.xz && \
  tar -xf Python-3.11.3.tar.xz && cd Python-3.11.3 && \
  CFLAGS=-fPIC ./configure --with-openssl-rpath=auto --enable-optimizations CFLAGS=-fPIC && \
  make -j$(nproc) && make altinstall && make install
# todo: update-alternatives may not be required
RUN update-alternatives --install /usr/bin/python python /usr/local/bin/python3.11 1 && \
  update-alternatives --install /usr/bin/pip pip /usr/local/bin/pip3.11 1 && \
  cp /usr/local/bin/python3.11 /usr/local/bin/python && \
  cp /usr/local/bin/pip3.11 /usr/local/bin/pip && \
  cp /usr/local/bin/pip3.11 /usr/local/bin/pip3

# required since ModuleNotFoundError: No module named 'pip' with nvidia pip packages, even if cli works
RUN wget "https://bootstrap.pypa.io/get-pip.py" && python get-pip.py --force-reinstall

# TensorRT9
# trt9.2 with whl since apt still only has 8.6
# https://github.com/samurdhikaru/TensorRT/blob/dev/release-9.0-EA/docker/ubuntu-22.04.Dockerfile
# todo: check what is required (needed for mlrt)
# TensorRT requires TensorRT https://github.com/NVIDIA/TensorRT/issues/85
RUN apt-get update && apt-get install -y --no-install-recommends libnvinfer8 libnvonnxparsers8 libnvparsers8 libnvinfer-plugin8 libnvinfer-dev libnvonnxparsers-dev \
  libnvparsers-dev libnvinfer-plugin-dev python3-libnvinfer tensorrt python3-libnvinfer-dev -yf --reinstall && apt-get autoclean -y && apt-get autoremove -y && apt-get clean -y
RUN apt-get install unzip wget git -y && wget https://pypi.nvidia.com/tensorrt-libs/tensorrt_libs-9.2.0.post12.dev5-py2.py3-none-manylinux_2_17_x86_64.whl \ 
        && mkdir tensorrt-wheel-9.2.0 \
        && unzip tensorrt_libs-9.2.0.post12.dev5-py2.py3-none-manylinux_2_17_x86_64.whl -d tensorrt-wheel-9.2.0 \
        && cp tensorrt-wheel-9.2.0/tensorrt_libs/*.so* /usr/lib/x86_64-linux-gnu \
        && cd /usr/lib/x86_64-linux-gnu \
        && ldconfig
# Install Cmake (TensorRT crashes with new cmake)
RUN cd /tmp && \
    wget https://github.com/Kitware/CMake/releases/download/v3.14.4/cmake-3.14.4-Linux-x86_64.sh && \
    chmod +x cmake-3.14.4-Linux-x86_64.sh && \
    ./cmake-3.14.4-Linux-x86_64.sh --prefix=/usr/local --exclude-subdir --skip-license && \
    rm ./cmake-3.14.4-Linux-x86_64.sh
# compiling
RUN git clone https://github.com/NVIDIA/TensorRT && cd TensorRT && git switch release/9.2 && git submodule update --init --recursive
RUN cd TensorRT && mkdir -p build && cd build && cmake .. -DTENSORRT_ROOT=/workspace/TensorRT -DTRT_LIB_DIR=/usr/lib/x86_64-linux-gnu -DGPU_ARCHS="60 61 70 75 80 86 87 89 90" -DTRT_OUT_DIR=`pwd`/out && make -j$(nproc) && make install

# ORT
# onnxruntime requires working tensorrt installation and thus can't be easily seperated into a seperate instance
# https://github.com/microsoft/onnxruntime/blob/main/dockerfiles/Dockerfile.tensorrt
ARG ONNXRUNTIME_REPO=https://github.com/Microsoft/onnxruntime
ARG ONNXRUNTIME_BRANCH=rel-1.16.3
ARG CMAKE_CUDA_ARCHITECTURES=37;50;52;60;61;70;75;80;89

RUN apt-get update &&\
    apt-get install -y sudo git bash unattended-upgrades
RUN unattended-upgrade

WORKDIR /code
ENV PATH /usr/local/nvidia/bin:/usr/local/cuda/bin:${PATH}

# cmake 3.28 (CMake 3.26 or higher is required)
RUN apt-get -y update && apt install wget && wget https://github.com/Kitware/CMake/releases/download/v3.28.0-rc1/cmake-3.28.0-rc1-linux-x86_64.sh  && \
    chmod +x cmake-3.28.0-rc1-linux-x86_64.sh  && sh cmake-3.28.0-rc1-linux-x86_64.sh  --skip-license && \
    cp /code/bin/cmake /usr/bin/cmake && cp /code/bin/cmake /usr/lib/cmake && \
    cp /code/bin/cmake /usr/local/bin/cmake && cp /code/bin/ctest /usr/local/bin/ctest && cp -r /code/share/cmake-3.28 /usr/local/share/ && \
    rm -rf cmake-3.28.0-rc1-linux-x86_64.sh 

# Prepare onnxruntime repository & build onnxruntime with TensorRT
# --parallel 6 for 6 compile threads, using all threads ooms my ram
RUN git clone --single-branch --branch ${ONNXRUNTIME_BRANCH} --recursive ${ONNXRUNTIME_REPO} onnxruntime &&\
    /bin/sh onnxruntime/dockerfiles/scripts/install_common_deps.sh &&\
    cd onnxruntime && PYTHONPATH=/usr/bin/python3 /bin/sh build.sh --parallel 6 --allow_running_as_root --build_shared_lib --cuda_home /usr/local/cuda \
      --cudnn_home /usr/lib/x86_64-linux-gnu/ --use_tensorrt --tensorrt_home /usr/lib/x86_64-linux-gnu/ --config Release --build_wheel --skip_tests --skip_submodule_sync --cmake_extra_defines '"CMAKE_CUDA_ARCHITECTURES='${CMAKE_CUDA_ARCHITECTURES}'"'

############################
# VSGAN
############################

# https://gitlab.com/nvidia/container-images/cuda/blob/master/dist/11.4.2/ubuntu2204/base/Dockerfile
FROM ubuntu:22.04 as base
ARG DEBIAN_FRONTEND=noninteractive
ENV NVARCH x86_64
ENV NVIDIA_REQUIRE_CUDA "cuda>=11.4"
COPY nvidia_icd.json /etc/vulkan/icd.d/nvidia_icd.json

LABEL maintainer "NVIDIA CORPORATION <cudatools@nvidia.com>"
RUN apt-get update && apt-get install -y --no-install-recommends \
  gnupg2 curl ca-certificates && \
  curl -fsSL https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/${NVARCH}/3bf863cc.pub | apt-key add - && \
  echo "deb https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/${NVARCH} /" >/etc/apt/sources.list.d/cuda.list && \
  apt-get purge --autoremove -y curl && \
  rm -rf /var/lib/apt/lists/*
RUN apt-get update && apt-get install -y --no-install-recommends \
  cuda-12-1 \
  cuda-cudart-12-1 \
  cuda-compat-12-1 && \
  rm -rf /var/lib/apt/lists/*
RUN echo "/usr/local/nvidia/lib" >>/etc/ld.so.conf.d/nvidia.conf && \
  echo "/usr/local/nvidia/lib64" >>/etc/ld.so.conf.d/nvidia.conf
ENV PATH /usr/local/nvidia/bin:/usr/local/cuda/bin:${PATH}
ENV LD_LIBRARY_PATH /usr/local/nvidia/lib:/usr/local/nvidia/lib64
ENV NVIDIA_VISIBLE_DEVICES all
ENV NVIDIA_DRIVER_CAPABILITIES compute,utility
ENV NVIDIA_DRIVER_CAPABILITIES all
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
  libx11-xcb-dev \
  libxkbcommon-dev \
  libwayland-dev \
  libxrandr-dev \
  libegl1-mesa-dev && \
  rm -rf /var/lib/apt/lists/*
# may not be required
ENV LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/local/cuda-12.0/lib64:/usr/local/cuda-12.0/lib
ENV NVIDIA_DRIVER_CAPABILITIES compute,utility
ENV NVIDIA_DRIVER_CAPABILITIES all

WORKDIR workspace

# install python
# https://stackoverflow.com/questions/75159821/installing-python-3-11-1-on-a-docker-container
# https://stackoverflow.com/questions/45954528/pip-is-configured-with-locations-that-require-tls-ssl-however-the-ssl-module-in
# /usr/local/lib/libpython3.11.a(longobject.o): relocation R_X86_64_PC32 against symbol `_Py_NotImplementedStruct' can not be used when making a shared object; recompile with -fPIC
# todo: test CFLAGS="-fPIC -march=native"
RUN apt update -y && apt install liblzma-dev libbz2-dev ca-certificates openssl libssl-dev libncurses5-dev libsqlite3-dev libreadline-dev libtk8.6 libgdm-dev \
  libdb4o-cil-dev libpcap-dev software-properties-common wget zlib1g-dev -y && \
  wget https://www.python.org/ftp/python/3.11.3/Python-3.11.3.tar.xz && \
  tar -xf Python-3.11.3.tar.xz && cd Python-3.11.3 && \
  CFLAGS=-fPIC ./configure --with-openssl-rpath=auto --enable-optimizations CFLAGS=-fPIC && \
  make -j$(nproc) && make altinstall && make install
# todo: update-alternatives may not be required
RUN update-alternatives --install /usr/bin/python python /usr/local/bin/python3.11 1 && \
  update-alternatives --install /usr/bin/pip pip /usr/local/bin/pip3.11 1 && \
  cp /usr/local/bin/python3.11 /usr/local/bin/python && \
  cp /usr/local/bin/pip3.11 /usr/local/bin/pip && \
  cp /usr/local/bin/pip3.11 /usr/local/bin/pip3
# required since ModuleNotFoundError: No module named 'pip' with nvidia pip packages, even if cli works
RUN wget "https://bootstrap.pypa.io/get-pip.py" && python get-pip.py --force-reinstall

# python shared (for ffmpeg)
RUN rm -rf Python-3.11.3 && tar -xf Python-3.11.3.tar.xz && cd Python-3.11.3 && \
  CFLAGS=-fPIC ./configure --enable-shared --with-ssl --with-openssl-rpath=auto --enable-optimizations CFLAGS=-fPIC && \
  make -j$(nproc)

# cmake
RUN apt-get -y update && apt install wget && wget https://github.com/Kitware/CMake/releases/download/v3.23.0-rc1/cmake-3.23.0-rc1-linux-x86_64.sh && \
  chmod +x cmake-3.23.0-rc1-linux-x86_64.sh && sh cmake-3.23.0-rc1-linux-x86_64.sh --skip-license && \
  cp /workspace/bin/cmake /usr/bin/cmake && cp /workspace/bin/cmake /usr/lib/x86_64-linux-gnu/cmake && \
  cp /workspace/bin/cmake /usr/local/bin/cmake && cp -r /workspace/share/cmake-3.23 /usr/local/share/

# zimg
# setting pkg version manually since otherwise 'Version' field value '-1': version number is empty
RUN apt-get install checkinstall -y
RUN apt install fftw3-dev python-is-python3 pkg-config python3-pip git p7zip-full autoconf libtool yasm ffmsindex libffms2-5 libffms2-dev -y && \
  git clone https://github.com/sekrit-twc/zimg --depth 1 --recurse-submodules --shallow-submodules && cd zimg && \
  ./autogen.sh && CFLAGS=-fPIC CXXFLAGS=-fPIC ./configure --enable-static --disable-shared && make -j$(nproc) && checkinstall -y -pkgversion=0.0 && \
  apt install /workspace/zimg/zimg_0.0-1_amd64.deb -y

# vapoursynth
RUN pip install --upgrade pip && pip install cython && git clone https://github.com/vapoursynth/vapoursynth && \
  cd vapoursynth && ./autogen.sh && \
  ./configure && make -j$(nproc) && make install && cd .. && ldconfig && \
  cd vapoursynth && python setup.py bdist_wheel

#################################################################
# pycuda
RUN pip install numpy && git clone https://github.com/inducer/pycuda --recursive && cd pycuda && python setup.py bdist_wheel

# color transfer
RUN pip install docutils pygments && git clone https://github.com/hahnec/color-matcher && cd color-matcher && python setup.py bdist_wheel

# vs-mlrt
# trt9.2 with whl since apt still only has 8.6
RUN apt-get install unzip wget git -y && wget https://pypi.nvidia.com/tensorrt-libs/tensorrt_libs-9.2.0.post12.dev5-py2.py3-none-manylinux_2_17_x86_64.whl \ 
        && mkdir tensorrt-wheel-9.2.0 \
        && unzip tensorrt_libs-9.2.0.post12.dev5-py2.py3-none-manylinux_2_17_x86_64.whl -d tensorrt-wheel-9.2.0 \
        && cp tensorrt-wheel-9.2.0/tensorrt_libs/*.so* /usr/lib/x86_64-linux-gnu \
        && cd /usr/lib/x86_64-linux-gnu \
        && ldconfig
COPY --from=TensorRT-ubuntu /TensorRT/build/out/libnvinfer_plugin.so* /TensorRT/build/out/libnvinfer_vc_plugin.so* /TensorRT/build/out/libnvonnxparser.so* /usr/lib/x86_64-linux-gnu/
COPY --from=TensorRT-ubuntu /usr/lib/x86_64-linux-gnu/libcudnn*.so*  /usr/lib/x86_64-linux-gnu/
RUN ln -s /usr/lib/x86_64-linux-gnu/libnvinfer.so.9 /usr/lib/libnvinfer.so
RUN ldconfig
RUN git clone https://github.com/NVIDIA/TensorRT && cd TensorRT && git switch release/9.2
ENV CPLUS_INCLUDE_PATH="/workspace/TensorRT/include"
# upgrading g++
RUN apt install build-essential manpages-dev software-properties-common -y && add-apt-repository ppa:ubuntu-toolchain-r/test -y && \
  apt update -y && apt install gcc-11 g++-11 -y && update-alternatives --install /usr/bin/gcc gcc /usr/bin/gcc-11 11 && \
  update-alternatives --install /usr/bin/g++ g++ /usr/bin/g++-11 11 && \
  # compiling
  git clone https://github.com/AmusementClub/vs-mlrt /workspace/vs-mlrt && cd /workspace/vs-mlrt/vstrt && mkdir build && \
  cd build && cmake .. -DVAPOURSYNTH_INCLUDE_DIRECTORY=/workspace/vapoursynth/include -D USE_NVINFER_PLUGIN=ON && make -j$(nproc) && make install 

# descale
RUN pip install meson ninja && git clone https://github.com/Irrational-Encoding-Wizardry/descale && cd descale && meson build && ninja -C build && ninja -C build install 

########################
# vs plugins
# Vapoursynth-VFRToCFR
RUN git clone https://github.com/Irrational-Encoding-Wizardry/Vapoursynth-VFRToCFR && cd Vapoursynth-VFRToCFR && \
  mkdir build && cd build && meson --buildtype release .. && ninja && ninja install

# vapoursynth-mvtools
RUN apt install nasm -y && git clone https://github.com/dubhater/vapoursynth-mvtools && cd vapoursynth-mvtools && ./autogen.sh && ./configure && make -j$(nproc) && make install 

# fmtconv
RUN git clone https://github.com/EleonoreMizo/fmtconv && cd fmtconv/build/unix/ && ./autogen.sh && ./configure && make -j$(nproc) && make install

# VMAF
RUN apt install nasm xxd -y && wget https://github.com/Netflix/vmaf/archive/refs/tags/v3.0.0.tar.gz && \
  tar -xzf v3.0.0.tar.gz && cd vmaf-3.0.0/libvmaf/ && \
  meson build --buildtype release -Denable_cuda=true -Denable_avx512=true && ninja -C build && \
  ninja -C build install && cd /workspace && rm -rf v3.0.0.tar.gz vmaf-3.0.0 && \
  git clone https://github.com/HomeOfVapourSynthEvolution/VapourSynth-VMAF && cd VapourSynth-VMAF && meson build && \
  ninja -C build && ninja -C build install

# MISC
RUN git clone https://github.com/vapoursynth/vs-miscfilters-obsolete && cd vs-miscfilters-obsolete && meson build && \
  ninja -C build && ninja -C build install

# akarin vs
RUN apt install llvm-15 llvm-15-dev -y && git clone https://github.com/AkarinVS/vapoursynth-plugin && \
  cd vapoursynth-plugin && meson build && ninja -C build && \
  ninja -C build install

# julek
RUN apt install clang libstdc++-12-dev -y
RUN git clone https://github.com/dnjulek/vapoursynth-julek-plugin --recurse-submodules -j8 && cd vapoursynth-julek-plugin/thirdparty && \
  mkdir libjxl_build && cd libjxl_build && cmake -C ../libjxl_cache.cmake -DCMAKE_CXX_COMPILER=clang++ -DCMAKE_C_COMPILER=clang -G Ninja ../libjxl && \
  cmake --build . && cmake --install . && cd ../.. && cmake -DCMAKE_C_FLAGS=fPIC -DCMAKE_CXX_FLAGS=-fPIC -DCMAKE_CXX_COMPILER=clang++ -B build -DCMAKE_BUILD_TYPE=Release -G Ninja && \
  cmake --build build && cmake --install build 

# warpsharp
RUN git clone https://github.com/dubhater/vapoursynth-awarpsharp2 && cd vapoursynth-awarpsharp2 && mkdir build && \
  cd build && meson ../ && ninja && ninja install

# CAS
RUN git clone https://github.com/HomeOfVapourSynthEvolution/VapourSynth-CAS && cd VapourSynth-CAS && meson build && \
  ninja -C build && ninja -C build install 

########################
# av1an
RUN apt install curl libssl-dev mkvtoolnix mkvtoolnix-gui clang-12 nasm libavutil-dev libavformat-dev libavfilter-dev -y && apt-get autoremove -y && apt-get clean
ENV PATH="/root/.cargo/bin:$PATH"

# av1an
# todo: use own custom av1an
RUN curl https://sh.rustup.rs -sSf | sh -s -- -y && \
  . $HOME/.cargo/env && \
  git clone https://github.com/master-of-zen/Av1an && \
  cd Av1an && cargo build --release --features ffmpeg_static && \
  mv /workspace/Av1an/target/release/av1an /usr/bin 

RUN git clone https://github.com/xiph/rav1e && \
  cd rav1e && \
  cargo build --release && \
  strip ./target/release/rav1e && \
  mv ./target/release/rav1e /usr/local/bin 

RUN git clone https://gitlab.com/AOMediaCodec/SVT-AV1/ && \
  cd SVT-AV1 && \
  sed -i 's/picture_copy(/svt_av1_picture_copy(/g' \
    Source/Lib/Common/Codec/EbPictureOperators.c \
    Source/Lib/Common/Codec/EbPictureOperators.h \
    Source/Lib/Encoder/Codec/EbFullLoop.c \
    Source/Lib/Encoder/Codec/EbProductCodingLoop.c && \
  cd Build && \
  cmake .. -G"Unix Makefiles" -DCMAKE_INSTALL_LIBDIR=lib -DBUILD_SHARED_LIBS=OFF -DCMAKE_BUILD_TYPE=Release && \
  make -j$(nproc) && make install 

RUN git clone --depth 1 https://aomedia.googlesource.com/aom && \
  cd aom && \
  mkdir build_tmp && cd build_tmp && cmake -DCMAKE_CXX_FLAGS="-O3 -march=native -pipe" -DBUILD_SHARED_LIBS=0 \
  -DENABLE_TESTS=0 -DENABLE_NASM=on -DCMAKE_INSTALL_LIBDIR=lib .. && make -j$(nproc) && make install

# pip
RUN MAKEFLAGS="-j$(nproc)" pip install timm wget cmake scipy mmedit meson ninja numba numpy scenedetect \
    pytorch-msssim thop einops kornia mpgg vsutil onnx && \
  pip install torch torchvision torchaudio --force-reinstall -U && \
  # installing pip version due to
  # ModuleNotFoundError: No module named 'torch_tensorrt.fx.converters.impl'
  pip install torch-tensorrt-fx-only==1.5.0.dev0 && \
  # holywu plugins currently only work with trt8.6
  pip install nvidia-pyindex tensorrt==8.6.1 && pip install polygraphy && rm -rf /root/.cache/

COPY --from=TensorRT-ubuntu /code/onnxruntime/build/Linux/Release/dist/onnxruntime_gpu-1.16.3-cp311-cp311-linux_x86_64.whl /workspace
RUN pip install coloredlogs flatbuffers numpy packaging protobuf sympy onnxruntime_gpu-1.16.3-cp311-cp311-linux_x86_64.whl

# holywu plugins
RUN git clone https://github.com/styler00dollar/vs-gmfss_union && cd vs-gmfss_union && pip install . && cd /workspace && rm -rf vs-gmfss_union
RUN git clone https://github.com/styler00dollar/vs-gmfss_fortuna && cd vs-gmfss_fortuna && pip install . && cd /workspace && rm -rf vs-gmfss_fortuna
RUN git clone https://github.com/styler00dollar/vs-dpir && cd vs-dpir && pip install . && cd .. && rm -rf vs-dpir
RUN pip install vsswinir vsbasicvsrpp --no-deps

# installing own versions
COPY --from=mmcv-ubuntu /mmcv/dist/ /workspace
COPY --from=cupy-ubuntu /cupy/dist/ /workspace
COPY --from=opencv-ubuntu /opencv-python/opencv*.whl /workspace
RUN pip uninstall -y mmcv* cupy* $(pip freeze | grep '^opencv' | cut -d = -f 1) && \
  find . -name "*whl" ! -path "./Python-3.11.3/*" -exec pip install {} \;

# installing onnx tensorrt with a workaround, error with import otherwise
# https://github.com/onnx/onnx-tensorrt/issues/643
# also disables pip cache purge
RUN git clone https://github.com/onnx/onnx-tensorrt.git && \
  cd onnx-tensorrt && \
  cp -r onnx_tensorrt /usr/local/lib/python3.11/dist-packages && \
  cd .. && rm -rf onnx-tensorrt

# workaround for arch updates
# ffmpeg: /usr/lib/x86_64-linux-gnu/libstdc++.so.6: version `GLIBCXX_3.4.32' not found (required by ffmpeg)
# ffmpeg: /usr/lib/x86_64-linux-gnu/libm.so.6: version `GLIBC_2.38' not found (required by ffmpeg)
# ffmpeg: /usr/lib/x86_64-linux-gnu/libc.so.6: version `GLIBC_2.38' not found (required by ffmpeg)
RUN mkdir /workspace/hotfix
WORKDIR /workspace/hotfix
RUN wget http://ftp.us.debian.org/debian/pool/main/libt/libtirpc/libtirpc-dev_1.3.4+ds-1_amd64.deb \
    http://ftp.us.debian.org/debian/pool/main/libx/libxcrypt/libcrypt-dev_4.4.36-2_amd64.deb \
    http://ftp.us.debian.org/debian/pool/main/libn/libnsl/libnsl-dev_1.3.0-3_amd64.deb \
    http://ftp.us.debian.org/debian/pool/main/libx/libxcrypt/libcrypt1_4.4.36-4_amd64.deb \
    http://ftp.us.debian.org/debian/pool/main/g/glibc/libc6_2.38-5_amd64.deb \
    http://ftp.us.debian.org/debian/pool/main/g/glibc/libc6-dev_2.38-5_amd64.deb \
    http://ftp.us.debian.org/debian/pool/main/g/glibc/libc-bin_2.38-5_amd64.deb \
    http://ftp.us.debian.org/debian/pool/main/g/glibc/libc-dev-bin_2.38-5_amd64.deb \
    http://ftp.us.debian.org/debian/pool/main/l/linux/linux-libc-dev_6.6.9-1_all.deb \
    http://ftp.us.debian.org/debian/pool/main/r/rpcsvc-proto/rpcsvc-proto_1.4.3-1_amd64.deb \
    http://ftp.us.debian.org/debian/pool/main/libt/libtirpc/libtirpc3_1.3.4+ds-1_amd64.deb

############################
# final
############################
FROM nvidia/cuda:12.1.1-runtime-ubuntu22.04 as final
# maybe official tensorrt image is better, but it uses 20.04
#FROM nvcr.io/nvidia/tensorrt:23.04-py3 as final
ARG DEBIAN_FRONTEND=noninteractive
ENV NVIDIA_VISIBLE_DEVICES all
ENV NVIDIA_DRIVER_CAPABILITIES all

WORKDIR workspace

# due to cupy jitify
# cub/detail/detect_cuda_runtime.cuh(39): warning: cuda_runtime_api.h: [jitify] File not found
# ../util_type.cuh(42): warning: cuda.h: [jitify] File not found
RUN apt update -y && apt install cuda-cudart-dev-12-1 linux-libc-dev -y

# install python
COPY --from=base /usr/local/bin/python /usr/local/bin/
COPY --from=base /usr/local/lib/python3.11 /usr/local/lib/python3.11
COPY --from=base /workspace/Python-3.11.3/libpython3.11.so* /workspace/Python-3.11.3/libpython3.so \
  /workspace/Python-3.11.3/libpython3.so /usr/lib

# vapoursynth
COPY --from=base /workspace/zimg/zimg_0.0-1_amd64.deb zimg_0.0-1_amd64.deb
RUN apt install ./zimg_0.0-1_amd64.deb -y && rm -rf zimg_0.0-1_amd64.deb

COPY --from=base /usr/local/lib/vapoursynth /usr/local/lib/vapoursynth
COPY --from=base /usr/local/lib/x86_64-linux-gnu/vapoursynth /usr/local/lib/x86_64-linux-gnu/vapoursynth
COPY --from=base /usr/local/lib/libvapoursynth-script.so* /usr/local/lib/libvapoursynth.so /usr/local/lib/

# vapoursynth
COPY --from=base /usr/local/bin/vspipe  /usr/local/bin/vspipe

# vs plugins
COPY --from=base /usr/local/lib/libvstrt.so /usr/local/lib/libmvtools.so /usr/local/lib/libfmtconv.so /usr/local/lib/
COPY --from=base /usr/lib/x86_64-linux-gnu/libfftw3f.so* /usr/lib/x86_64-linux-gnu/

COPY --from=bestsource-lsmash-ffms2-vs /usr/local/lib/liblsmash.so* /usr/local/lib/
COPY --from=bestsource-lsmash-ffms2-vs /workspace/L-SMASH-Works/VapourSynth/build/libvslsmashsource.so /workspace/bestsource/build/libbestsource.so /usr/local/lib/vapoursynth
COPY --from=bestsource-lsmash-ffms2-vs /workspace/ffms2/src/core/.libs/libffms2.so* /usr/lib/x86_64-linux-gnu/

COPY --from=base /usr/local/lib/vapoursynth/libvmaf.so /usr/local/lib/vapoursynth/libdescale.so /usr/local/lib/vapoursynth/libakarin.so \
  /usr/local/lib/vapoursynth/libmiscfilters.so /usr/local/lib/vapoursynth/libjulek.so /usr/local/lib/vapoursynth/libcas.so /usr/local/lib/vapoursynth/

COPY --from=base /usr/local/lib/x86_64-linux-gnu/vapoursynth/libvfrtocfr.so /usr/local/lib/x86_64-linux-gnu/libvmaf.so /usr/local/lib/x86_64-linux-gnu/vapoursynth/libvfrtocfr.so \
  /usr/local/lib/x86_64-linux-gnu/libvmaf.so /usr/local/lib/x86_64-linux-gnu/libawarpsharp2.so /usr/local/lib/x86_64-linux-gnu/

# av1an / rav1e / svt / aom
COPY --from=base /usr/bin/av1an /usr/local/bin/rav1e /usr/bin/
COPY --from=base /usr/local/bin/SvtAv1EncApp /usr/local/bin/SvtAv1DecApp /usr/local/bin/aomenc /usr/local/bin/
# ffmpeg
COPY --from=ffmpeg-arch /home/makepkg/FFmpeg/ffmpeg /usr/local/bin/ffmpeg

# windows hotfix
RUN rm -rf /usr/lib/x86_64-linux-gnu/libnvidia-ml.so.1 /usr/lib/x86_64-linux-gnu/libcuda.so.1 \
  /usr/lib/x86_64-linux-gnu/libnvcuvid.so.1 /usr/lib/x86_64-linux-gnu/libnvidia* /usr/lib/x86_64-linux-gnu/libcuda*

# trt
COPY --from=TensorRT-ubuntu /TensorRT/build/out/libnvinfer_plugin.so* /TensorRT/build/out/libnvinfer_vc_plugin.so* /TensorRT/build/out/libnvonnxparser.so* /usr/lib/x86_64-linux-gnu/
COPY --from=TensorRT-ubuntu /usr/lib/x86_64-linux-gnu/libcudnn*.so* /usr/lib/x86_64-linux-gnu/libnvinfer.so* /usr/lib/x86_64-linux-gnu/libnvinfer_builder_resource.so* \
  /usr/lib/x86_64-linux-gnu/libnvonnxparser.so* /usr/lib/x86_64-linux-gnu/libnvparsers.so.8* /usr/lib/x86_64-linux-gnu/libnvinfer_plugin.so.8* /usr/lib/x86_64-linux-gnu/

# ffmpeg (todo: try to make it fully static)
COPY --from=base /usr/lib/x86_64-linux-gnu/libxcb*.so* /usr/lib/x86_64-linux-gnu/libgomp*.so* /usr/lib/x86_64-linux-gnu/libfontconfig.so* \
  /usr/lib/x86_64-linux-gnu/libfreetype.so* /usr/lib/x86_64-linux-gnu/libfribidi.so* /usr/lib/x86_64-linux-gnu/libharfbuzz.so* /usr/lib/x86_64-linux-gnu/libxml2.so* \
  /usr/lib/x86_64-linux-gnu/libsoxr.so* /usr/lib/x86_64-linux-gnu/libXau.so* /usr/lib/x86_64-linux-gnu/libXdmcp.so* \
  /usr/lib/x86_64-linux-gnu/libexpat.so* /usr/lib/x86_64-linux-gnu/libpng16.so* /usr/lib/x86_64-linux-gnu/libbrotlidec.so* /usr/lib/x86_64-linux-gnu/libglib-2.0.so* /usr/lib/x86_64-linux-gnu/libgraphite2.so* \
  /usr/lib/x86_64-linux-gnu/libicuuc.so* /usr/lib/x86_64-linux-gnu/libbsd.so* /usr/lib/x86_64-linux-gnu/libbrotlicommon.so* /usr/lib/x86_64-linux-gnu/libicudata.so* \
  /usr/lib/x86_64-linux-gnu/libicudata.so* /usr/lib/x86_64-linux-gnu/libmd.so* /usr/lib/x86_64-linux-gnu/libdrm.so* \
  /usr/lib/x86_64-linux-gnu/
COPY --from=ffmpeg-arch /usr/lib/libstdc++.so* /usr/lib/x86_64-linux-gnu/

# opencv
COPY --from=base /usr/lib/x86_64-linux-gnu/libGL.so* /usr/lib/x86_64-linux-gnu/libgthread-2.0.so* /usr/lib/x86_64-linux-gnu/libGLdispatch.so* \
  /usr/lib/x86_64-linux-gnu/libGLX.so* /usr/lib/x86_64-linux-gnu/libX11.so* /usr/lib/x86_64-linux-gnu/

# move trtexec so it can be globally accessed
COPY --from=TensorRT-ubuntu /TensorRT/build/out/trtexec /usr/bin

# ffmpeg hotfix
COPY --from=base /workspace/hotfix/* /workspace
RUN dpkg --force-all -i *.deb  && rm -rf *deb

RUN ldconfig

ENV CUDA_MODULE_LOADING=LAZY
WORKDIR /workspace/tensorrt
