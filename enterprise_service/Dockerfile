    FROM python:3.8

    RUN mkdir -p ~/.config/pip && \
        echo \
        "[global]\n" \
        "no-cache-dir = true\n" \
        "trusted-host = 172.21.100.15\n" \
        "index = http://172.21.100.15:8081/repository/pypi-all/pypi\n" \
        "index-url = http://172.21.100.15:8081/repository/pypi-all/simple" \
        > ~/.config/pip/pip.conf

    # avoid-extension-reinstalls
    RUN mkdir -p /root/.vscode-server/extensions
    
    # install valkka/onvif
    WORKDIR /root
    RUN apt-get update && \ 
        git clone https://github.com/elsampsa/valkka-core.git && \ 
        cd valkka-core && \
        apt-get install -y mesa-utils glew-utils python3-numpy \ 
        python3-pip v4l-utils openssl build-essential yasm cmake \ 
        pkg-config swig libglew-dev mesa-common-dev python3-dev \ 
        libasound2-dev libssl-dev coreutils freeglut3-dev && \ 
        pip install numpy && \
        cd ext && \
        ./download_ffmpeg.bash && \
        cd .. && \
        ./easy_build.bash && make -f debian/rules package && \
        cd build_dir && \
        dpkg -i Valkka-*.deb && apt-get -fy install && \
        rm -r /root/valkka-core
    
    # install requirements.txt and onvif_zeep for service
    WORKDIR /usr/src/app/enterprise_manager
    COPY requirements.txt ./
    RUN python -m pip install --no-cache-dir --upgrade -r requirements.txt && rm requirements.txt && pip install --upgrade onvif_zeep
    RUN apt-get install -y iputils-ping && rm -rf /var/lib/apt/lists/*
    
    # copy source folder and set pythonpath environment
    COPY enterprise_manager .
    ENV TZ Asia/Ho_Chi_Minh
    ENV PYTHONPATH "${PYTHONPATH}:/usr/lib/python3/dist-packages:/usr/local/lib/python3.8/site-packages/"

    CMD [ "bash", "-c", "python main.py" ]