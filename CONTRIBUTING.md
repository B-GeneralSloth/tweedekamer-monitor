# Contributing to Tweede Kamer Monitor

This guide walks you through contributing with GitHub, Conda, the Streamlit dashboard, and the local DuckDB pipeline. The project uses `dlt` to load raw data into DuckDB and `dbt` to build the `silver` tables. Exploratory notebooks are in `eda/`.

## 1. Fork and clone

On [GitHub](https://github.com/afvanwoudenberg/tweedekamer-monitor), click **Fork** to create your own copy. Replace `YOUR-GITHUB-NAME` below with your GitHub username.

Clone your fork:

```bash
git clone https://github.com/YOUR-GITHUB-NAME/tweedekamer-monitor.git
```

Enter the project folder:

```bash
cd tweedekamer-monitor
```

Connect your clone to the main project so you can get updates:

```bash
git remote add upstream https://github.com/afvanwoudenberg/tweedekamer-monitor.git
```

## 2. Create the Conda environment

Install Miniforge or another Conda distribution if needed. From the project folder, create the environment defined in `environment.yml`:

```bash
conda env create --file environment.yml
```

Activate it:

```bash
conda activate tweedekamer_monitor
```

If `environment.yml` changes later, update the environment:

```bash
conda env update --name tweedekamer_monitor --file environment.yml
```

Activate it again in each new terminal:

```bash
conda activate tweedekamer_monitor
```

## 3. Configure notebook output cleaning

Run this once in each clone, with the Conda environment active:

```bash
nbstripout --install --attributes .gitattributes
```

This configures Git to remove notebook outputs when you stage `.ipynb` files. It does not clear outputs from the notebook open in Jupyter or VS Code.

## 4. Create a branch

Update your local `main` from the main project:

```bash
git switch main
```

```bash
git pull upstream main
```

Push the updated `main` to your fork:

```bash
git push origin main
```

Create a branch for your change:

```bash
git switch -c describe-your-change
```

Use a short name that describes your work, for example `fix-notebook-query`.

## 5. Work and test

To run the dashboard from the repository root:

```bash
streamlit run app/app.py
```

To open the exploratory notebooks:

```bash
jupyter lab
```

In VS Code, select the `tweedekamer_monitor` kernel if prompted. The notebooks use the local `tweedekamer.duckdb` database in the project folder. This database is ignored by Git.

To run a small pipeline test using two feed pages:

```bash
python pipeline/run_pipeline.py --max-pages 2
```

To run the full pipeline, which reads the live public feed:

```bash
python pipeline/run_pipeline.py
```

## 6. Update your branch

Before opening a pull request, get the latest changes from the main project:

```bash
git switch main
```

```bash
git pull upstream main
```

```bash
git push origin main
```

Return to your work branch:

```bash
git switch describe-your-change
```

Merge the latest `main` into it:

```bash
git merge main
```

## 7. Commit and open a pull request

Check your changes:

```bash
git status
```

Stage the files you changed. Replace the example path with the path to your file:

```bash
git add path/to/changed-file
```

Commit with a short description:

```bash
git commit -m "Describe the change"
```

Push your branch to your fork:

```bash
git push -u origin describe-your-change
```

On GitHub, open your fork and click **Compare & pull request**. Describe what you changed and how you tested it, then submit the pull request to the main project. If changes are requested, commit and push them to the same branch; the pull request will update automatically.
