models/weapons2/railgun/railgun2
{
	sort additive
	cull disable
	{
		map	models/weapons2/railgun/railgun2.glow.tga
		blendfunc GL_ONE GL_ONE
		rgbGen entity	// identity
	}
}

models/weapons2/railgun/railgun4
{   
	{
		map models/weapons2/railgun/railgun4.tga
                tcMod scroll 0.3 0.05
                blendfunc blend
                rgbGen identity
	}
	{
		map models/weapons2/railgun/railgun5.tga
                tcmod rotate 33
                tcMod scroll .7 3
                blendfunc add
                rgbGen identity
	}
        {
		map models/weapons2/railgun/railgun6.tga
		tcGen environment
                tcMod scroll 0 2
		blendfunc add
		rgbGen identity
	} 
}

models/weapons2/railgun/railgun3
{
	qer_editorimage models/weapons2/railgun/railgun3
	{
		map models/weapons2/railgun/railgun3.tga
		rgbGen lightingDiffuse
	}
	{
		map $lightmap 
		blendfunc filter
		rgbGen identity
	}
	{
		map models/weapons2/railgun/railgun3a.tga
		blendfunc add
		depthFunc equal
	}
	{
		map models/weapons2/railgun/railgun3b.tga
		blendfunc add
		rgbGen wave sin .8 0.5 .8 2
		depthFunc equal
	}
	{
		map models/weapons2/railgun/railgun3b1.tga
		blendfunc add
		rgbGen wave sin .8 0.5 .8 1
		depthFunc equal
	}
	{
		map models/weapons2/railgun/railgun3c.tga
		blendfunc add
		rgbGen wave sin .8 0.5 .8 1 
		depthFunc equal
	}
}