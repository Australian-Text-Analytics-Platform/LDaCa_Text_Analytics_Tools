## LDaCA Binder Repository Guide

- This root repository exists to build and launch Binder for the `ldaca_web_app` submodule. Treat the application code as owned by `ldaca_web_app/`; the root should stay focused on Binder bootstrap, launch, and publishing.
- Binder-owned root files are `binder/`, `ldaca_web_app_launch.ipynb`, `README.md`, `pyproject.toml`, `.gitmodules`, and `.github/workflows/repo2docker-dockerhub.yml`.
- When installing Python dependencies from the root, target the concrete submodule packages under `./ldaca_web_app/` rather than old root-level package paths.
- The notebook launcher starts backend helpers from `ldaca_web_app_backend` and serves frontend assets from `ldaca_web_app/frontend/build`.
- Keep root documentation short and Binder-specific. Do not duplicate backend, frontend, or desktop documentation that now lives in the submodule.
- Keep Binder automation compatible with repo2docker: environment setup belongs in `binder/environment.yml`, system packages in `binder/apt.txt`, and runtime provisioning in `binder/postBuild`.
- The generated `binder/Dockerfile` is a published-image pointer managed by the root workflow; avoid adding unrelated logic there.

### Detailed instructions

- `.github/instructions/python.instructions.md`
- `.github/instructions/langchain-python.instructions.md`
- `.github/instructions/playwright-python.instructions.md`
- `.github/instructions/security-and-owasp.instructions.md`
- `.github/instructions/performance-optimization.instructions.md`
- `.github/instructions/ai-prompt-engineering-safety-best-practices.instructions.md`