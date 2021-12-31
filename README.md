# CClear Compiler
A language designed to have the speed and functionality of c++ but that is both easier and faster to read and write! CClear is a wrapping language that compiles directly into *.cpp* and *.h* files.

I'm looking for anyone who may have an opinion on the syntax, especially junior and experienced C++ devs, for second opinions. The syntax will still be subject to my judgment overall, but it's still in its infancy so it has a high capacity to change. You might be able to tell that I have a small bias to Python. If you don't like that you better let me know quick!

## Roadmap

- [X] Variable declarations
- [ ] If statements
- [ ] Functions
- [ ] Classes
- [ ] Inherits / Compiler instructions
- [ ] Good error messages
- [ ] Automatically handle C++ compilation


## Installation

Installation assumes you already have *python3* and *pip3* installed.
```
git clone git@github.com:blaze-the-star/cclear-compiler.git
cd cclear-compiler
pip3 install -r requirements.txt
```

## Run Compiler

To compile a *.cclr* file to *.cpp* and *.h* files run the following command.

```
python3 Compiler.py -s you_script.cclr
```

By default this will create a *\_\_cclearcache\_\_* folder with all of the *.cpp* and *.h* files at your terminal's current directory. To change where this folder is generated you can use *-w* to specify the folder in which to generate the *\_\_cclearcache\_\_* folder, ideally your project folder.

```
python3 Compiler.py -s you_script.cclr -w optionaly_add_a/path_to/your_workspace
```
With that the C++ code is ready to be compiled!

## Code Example

As of now it only compiles variable declarations, but that means that it technically compiles 100% valid C++ code! Below is a mock example of how I currently envision CClear's syntax in addition to what I'd expect it to compile to.

from CClear
```js
class MyObject;

	alc data:int = 100;

	def somthing_very_important(param1:int, param2:bool) : int;
		if param2;
			return other(2, 6845);
		else;
			data = param1 + data;
			return data;
			
	def other(a:int, b:int) : int;
		return a + b
			
class ItsObject(public) : MyObject;
			
	def somthing_very_important(param1:int, param2:bool) : int;
		if param2;
			return param1;
		else;
			return 0;
			
def main() : int;
	alc obj:MyObject = MyObject();
	obj.somthing_very_important(3, false);
	
	return 0;
```

to C++
```cpp
# ================
# === Cpp file ===
# ================

int MyObject::somthing_very_important(int param1, bool param2)
{
	if (param2)
	{
		return other(2, 6845);
	}
	else
	{
		data = param1 + data;
		return data;
	}
}
	
int MyObject::other(int a, int b)
{
	return a + b;
}
			
int ItsObject::somthing_very_important(int param1, bool param2)
{
	if (param2);
	{
		return param1;
	}
	else:
	{
		return 0;
	}
}

int main()
{
	MyObject obj;
	obj::somthing_very_important(3, false)
	
	return 0;
}

# ===================
# === Header file ===
# ===================

class MyObject
{
	int data = 100;
	int somthing_very_important(int param1, bool param2);
	int other(int a, int b);
};
			
class ItsObject : MyObject BaseClass
{	
	int somthing_very_important(int param1, bool param2);
};
```











