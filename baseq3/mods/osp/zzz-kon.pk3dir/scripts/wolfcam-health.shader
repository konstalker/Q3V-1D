models/powerups/health/sphere_orange
{
	{
		map textures/effects/envmapgold.tga
		tcGen environment
		tcmod rotate 44
		tcmod scroll 2 2
		blendfunc add
	}
}

models/powerups/health/sphere_blue
{
	{
		map textures/effects/mhealth_sphere.tga
		tcmod rotate 45
		tcmod scroll 3 2
		tcGen environment
		blendfunc add
	}
}

models/powerups/health/sphere_green
{
	{
		map textures/effects/envmaprail.tga
		tcmod rotate 45
		tcmod scroll 3 2
		tcGen environment
		blendfunc GL_ONE GL_ONE
	}
}

models/powerups/health/sphere
{
	{
		map textures/effects/tinfx2c.tga
		tcmod rotate 45
		tcmod scroll 3 2
		tcGen environment
		blendfunc GL_ONE GL_ONE
	}
}

models/powerups/health/hp_small
{
	
	{
		map models/powerups/health/green.tga
		tcGen environment
		blendfunc GL_ONE GL_ZERO
		rgbGen identity
	}
	{
		map models/powerups/health/hp_small.tga
		blendfunc blend
		rgbGen lightingDiffuse
	}
}

models/powerups/health/hp_med
{
	
	{
		map models/powerups/health/yellow.tga
		tcGen environment
		blendfunc GL_ONE GL_ZERO
		rgbGen identity
	}
	{
		map models/powerups/health/hp_small.tga
		blendfunc blend
		rgbGen lightingDiffuse
	}
}

models/powerups/health/hp_large
{	
	
	{
		map models/powerups/health/orange.tga
		tcGen environment
		blendfunc GL_ONE GL_ZERO
		rgbGen identity
	}
	{
		map models/powerups/health/hp_small.tga
		blendfunc blend
		rgbGen lightingDiffuse
	}

}

models/powerups/health/hp_mega
{
	{
		map models/powerups/health/blue.tga
		tcGen environment
		blendfunc GL_ONE GL_ZERO
		rgbGen identity
    }
	{
	    map models/powerups/health/hp_small.tga
		blendfunc blend
        rgbGen lightingDiffuse
    }
}

