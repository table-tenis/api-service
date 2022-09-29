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

    WORKDIR /usr/src/app
    COPY register/requirements.txt ./
    RUN pip install --no-cache-dir -r requirements.txt && rm requirements.txt
    ENV TZ Asia/Ho_Chi_Minh

    COPY enterprise_manager enterprise_manager

    CMD [ "bash", "-c", "python enterprise_manager/main.py" ]