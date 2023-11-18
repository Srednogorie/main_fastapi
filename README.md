1. Create local certificates, they can be used for every next local project
mkcert -cert-file local-docker-cert.pem -key-file local-docker-key.pem "docker.localhost" "*.docker.localhost" "domain.local" "*.domain.local" "127.0.0.1" "0.0.0.0"mkcert -cert-file local-docker-cert.pem -key-file local-docker-key.pem "docker.localhost" "*.docker.localhost" "domain.local" "*.domain.local" "127.0.0.1" "0.0.0.0"
2. Choose name of your app, create local DB using it and then update settings.py and compose.yml using the same name.
3. Create .env.dev fille and setup env variables, you will need at least BD_USER, BD_PASSWORD, DB_PORT & DB_ADDRESS.
4. If using vscode in launch.json use the following snippet.
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: Remote Attach",
            "type": "python",
            "request": "attach",
            "port": 5678,
            "host": "localhost",
            "pathMappings": [
                {
                    "localRoot": "${workspaceFolder}",
                    "remoteRoot": "."
                }
            ]
        }
    ]
}
5. run "docker compose up development" then start the vscode launch configuration. The project is now available through https at port 8000 