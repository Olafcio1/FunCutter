# ✂️ FunCutter
An ugly super-fast multi-version project file patcher.<br/>
Alternative to Stonecutter. Almost no setup.

## 🔼 Setup
1. Create a file called `build.funcutter` in your project root directory.<br/>
   Its contents may be for example this:

    ```text
    # 1.20.1
    minecraft_version=1.20.1
    yarn_mappings=1.20.1+build.10
    loader_version=0.16.3
    fabric_version=0.92.2+1.20.1
    ```

    If you're not sure what to put there, just copy this segment from the `gradle.properties` file.

    No magic here:<br/>
    If your project previously depended on manual code changes for each version you want to build, you can almost copy-paste into it.

2. Create a directory called `versions` in your project root directory.<br/>
   You can create subdirectories named after versions there, which contain the patch files (and even more directories).

3. Install FunCutter<br/>
   1. Download the source code
   2. Install Python 3.11 <u>with an EXE installer</u>
      - with the **Add to PATH** option selected
      - with the **Use admin privileges** option **un**selected
   3. In FunCutter's source code, double-click the `install.py` script
   4. In the project root, run `funcutter`

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
