# Compiling for Windows 10 and above
You should first install [Visual Studio](https://visualstudio.microsoft.com/). The following process has been adapted for Visual Studio  Community 2019.


## Installing dependencies: GNU Scientific Librairy
The easiest way to install GSL is throught the windows VC package manager (vcpkg).

### Installing git
Install git for Windows from [https://git-scm.com/](https://git-scm.com/).

### Installing [vcpkg](https://github.com/microsoft/vcpkg)
vcpkg is a C++ library manager for Windows.

Open PowerShell and copy/paste the following commands to install vcpkg :
```
cd C:\
mkdir DEV
cd DEV
git clone https://github.com/microsoft/vcpkg.git
cd vcpkg
.\bootstrap-vcpkg.bat -disableMetrics
.\vcpkg integrate install
```
If the last command doesn't work, it's because you don't have the admin rights. Don't worry there is a work around.

### Installing GNU Scientific Library
Then install GNU Scientific Library:
```
.\vcpkg install gsl:x86-windows
.\vcpkg install gsl:x64-windows
```

If you don't have the admin rights, the gsl lib won't be linked to Visual Studio automaticly.
After loading the project in Visual Studio (see next section), you will have to create a NuGet package of the library and then to import it (here we're doing a package for both 32 and 64 bits versions):
```
.\vcpkg export gsl:x64-windows gsl:x86-windows --nuget --nuget-id=openetrandeps --nuget-version=1.0.0
```

Then in Visual Studio, go to *Tool/NuGet Package Manager/Package Manager Console*. Paste the last line of the PowerShell in the new console window in Visual Studio.
```
Install-Package openetrandeps -Source "C:\DEV\vcpkg"
```

## Compiling with Visual Studio
Launch Visual Studio and then open a new project: *File/New/Project From Existing Code...*

Import the GSL NuGet package if vcpkg is not installed with admin rights (see previous section).

Open the Project Property Pages under *Project/Properties*, select the configuration [Debug|Release] and the platform [Win32|x64].

To compile, launch *Build/Build solution*

### Adding a hook for post-compiling tests
Open the Project Property Pages under *Project/Properties*, under Configuration Properties/Debuging, modify the options "Command", "Command Arguments" and "Working Directory".

Example:
- Command           = $(TargetPath)
- Command Arguments = -plot none $(SolutionDir)\Tests\test.dat
- Working Directory = $(ProjectDir)
