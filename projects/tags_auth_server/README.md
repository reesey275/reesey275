# Tags Auth Server

Tags Auth Server explores simple tag-based authorization for web services. Users receive labels such as `admin`, `editor`, or `viewer` that determine access to different APIs. The idea is to keep the rules lightweight and easy to update without redefining roles. Development is still early; I'm drafting the endpoint design and deciding on a database. A future milestone is building a Dockerized demo that integrates with [OAuth 2.0](https://oauth.net/2/).

## Scripts

- `scripts/setup.sh` – initializes the tags_auth_server environment.
