# ✂️ FunCutter
An ugly super-fast multi-version project file patcher.<br/>
Alternative to Stonecutter. Almost no setup.

## 🔼 Setup
1. Install FunCutter<br/>
   1. Download the source code
   2. Install Python 3.11 <u>with an EXE installer</u>
      - with the **Add to PATH** option selected
      - with the **Use admin privileges** option **un**selected
   3. In FunCutter's source code, double-click the `install.py` script

2. Run `funcutter init` in your project root

3. Create a directory called `versions` in your project root directory.<br/>
   You can create subdirectories named after versions there, which contain the patch files (and even more directories).

## 🪴 Usage
- To build your project for all specified versions, you can just run `funcutter`.<br/>
  You can specify the options and the task name if you need them - e.g.:

  |           Command           |      Later in Gradle      |
  |-----------------------------|---------------------------|
  | `funcutter build`           | `gradlew build`           |
  | `funcutter --offline`       | `gradlew build --offline` |
  | `funcutter build --offline` | `gradlew build --offline` |

- To check out your project for each of the specified versions, you can use `funcutter !wait`.<br/>
  For each of the versions, it:
  1. does the patches,
  2. lets you see the code,
  3. undoes the patches,
  4. proceeds to the next version.

  If you want to change a thing during the process, you can amend commit it.<br/>
  It will add the change to the funcutter temporary commit, which will stay for the next versions during the process, and end up in your unstaged working root after all versions are processed.

## 🕍 Syntax
FunCutter supports multiple types of files:
- **File Patch (.fp-\*)**<br/>
  An example `.fp-java` file may look like this:

```java
{
    State.legacy = false;  // This is the searched text
    State.legacy = true;   // This is the replacement
}
```

  The first search result is replaced with the replacement.<br/>
  The search can have only one line, however the replacement can have multiple lines.

- **File Script (.fs-\*)**<br/>
  An example `.fs-json` file may look like this:

```python
# Appends the 'ClientConnectionMixin' string
# to the 'client' array
this['client'].append("ClientConnectionMixin")
```

  This format is entirely based on Python - as it uses it.<br/>
  This can be useful when e.g. adding a mixin.


- **File Delete (.fd-\*)**<br/>
  These files are empty, and indicate the removal of a file.<br/>
  For example, creating a file called `ModernMixin.fd-java` indicates the removal of the file `ModernMixin.java`.

There might be more filetypes available in the future.
