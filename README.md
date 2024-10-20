Blender OBJ to Sonic the Fighters 3D Converter

This converter is dedicated, in respect and admiration, to the spirit that lives in the computer.

How to use:
1. Open up the example blend file to see a familiar face:
![image](https://github.com/user-attachments/assets/5246f0c2-d922-4ad3-a4bb-a955781f94f4)

We will be replacing Sonic's Idle Right head with this one.
If you're repeating these steps with your own model, make sure it's mostly made of quads rather than triangles. Triangles will work, but they're less efficient than quads, so they should only be used to add artistic flare. If your whole model is triangulated, use the tris -> quads feature in Blender, otherwise your model will take up double the space in memory than it should.

Next we will discuss how to assign legal materials.

2. On the right in the materials panel, you will see that Mario has some weirdly named materials assigned for each color:
![image](https://github.com/user-attachments/assets/980e1aa3-0050-443f-806f-37669fff50d2)

The colors of these materials do not matter. You can make 805E purple instead of red, and in-game it will still show up as red. The reason for this is that the color is actually determined by the hexadecimal name itself. 805E represents an address in memory for this material, so changing it to red is only done for preview purposes. To see a full visual dictionary of possible colors and their addresses, see the google doc here: https://docs.google.com/document/d/1KaK18JuTN9-ijWS-Qq6Xv_wQbQp57sIowCMuld8FZ0w/edit?tab=t.0

Scroll down to the pictures of Sonic's head as different colors. The hexadecimal address in bold is what you will name your material to apply that color in-game.

3. Now we're ready to export. Select your model in Object Mode then  Go to File -> Export -> Wavefront (.obj)

![image](https://github.com/user-attachments/assets/9b90ff58-3c27-4a76-839a-94eb5e2f0d66)

The important things to note here are: 
* "Selected Only" checkbox is CHECKED
* Forward Axis is -X
* Up Axis is -Z
* "Triangulated Mesh" is UNCHECKED

Export it as in.obj next to the converter.py script.

4. Open PowerShell or Command Prompt next to converter.py and type "python3 converter.py" to convert in.obj to out.stfmdl and out.stfmat

![image](https://github.com/user-attachments/assets/1438f81c-ba7a-40b7-ad59-9794b80f646c)

This portion will become more refined and accessible to non-technical people as time goes on. For now, it's important to understand what's happening here.

In the converter's main function, it opens the OBJ and does the conversions to the Sonic the Fighters 3D format. This part is completely automated, but feel free to change "out" to the name of the model that you plan to distribute. Next are the 2 addresses printed out to the screen. These contain valuable information on how to inject the model.

addr_to_model_ptr takes in an address from ROM_POL and converts it to an address the pointer table in ROM_DATA will understand.

addr_to_mat_ptr takes in an address from ROM_TEX and converts it to an address the pointer table in ROM_DATA will understand.

The current addresses I have pre-filled, 0xEC2590 and 0x7B45E0 are both towards the end of each of these files where there's mostly garbage bytes and shouldn't affect anything in-game.

Next we will put our model and our material at these addresses.

5. Open ROM_POL.bin in HxD or any hex editor.

Go to View -> Byte Group Size -> 4 to make things easier to read.
Press CTRL + G and type in EC2590, where we're going to tell the pointer table to look for the Sonic Idle Right head model

![image](https://github.com/user-attachments/assets/a0304575-8d80-40f1-84de-dfdd9580d19c)

I've already pasted the bytes in here, but yours will says "FFFFFFFF" repeatedly. Put your cursor at 0xEC2590, open out.stfmdl in Notepad, press CTRL + A then CTRL + C, then back in HxD press CTRL + B to do a byte paste + replace. The numbers will turn red, and if you press CTRL + G and go back to EC2590, the bytes should look the same as mine with the model starting with 01040400.

Now we will do the same with our material.

6. Open ROM_TEX.bin in HxD and press CTRL + G to go to 7B45E0, where we're going to point the pointer table for the Sonic Idle Right head material.

  ![image](https://github.com/user-attachments/assets/01cee8b2-96ef-43de-811e-8f9e2aa9101c)

Open the out.stfmat in notepad and repeat the process with the bytes for the material. Again remember to use CTRL + B to paste so that we don't add any bytes to the file, we need to replace them.

Now we can edit the pointer table.

8. Open ROM_DATA.bin in HxD and press CTRL + G to go to EBD40. This is where the Sonic Idle Right head addresses are in the pointer table. We will be mapping out where everything is in the future, but in case you'd like to look for something specific, the pointer table points to models in the same order as the debug menu, so the Sonic Idle Left head is right before this one etc. There are 4 addresses per model and they're aligned like this:

![image](https://github.com/user-attachments/assets/07f3ee52-ebbd-445c-8877-2cc92d250046)

We're going to be editing the middle 2 addresses. I've already done this step, so your middle 2 addresses will be different from the picture. 
As you may have guessed, the print statements from earlier tell us what the pointer values should be in this table.

0xEC2590 becomes 6809BB00

0x7B45E0 becomes F0A23D00

The material comes first in the table, so we place it here:

![image](https://github.com/user-attachments/assets/aa4e7ef5-a056-4ba2-be7c-633ca897b833)

Then comes the model pointer, so we place it here:

![image](https://github.com/user-attachments/assets/9ab8498f-8d26-4410-b685-40a002ed3443)

9. We have now completed all the steps necessary for the model injection. If you start the game and you've used the example model, you will see this:

![image](https://github.com/user-attachments/assets/1ff3c0be-514a-4599-a721-a2dc6c08e76e)
![image](https://github.com/user-attachments/assets/3d7e9ec5-554b-4099-9bc0-20ef82b98f14)

As we streamline the tools, we will be creating a GUI to handle all of the injection and byte calculations to make sure everything is optimized and fits where it needs to, as well as create an easy-to-use system that will let you name an OBJ something like sonic_head_idle_right.stfmdl/.stfmat and have it take care of the rest for you. For now, if you're intent on creating art mods, please bear with us while we make them more user-friendly.

Thanks for reading, and we look forward to seeing what you all come up with!
