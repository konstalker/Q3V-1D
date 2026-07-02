menuback
{
	nomipmaps
	{
		map NewWallpaper/Background.tga
	}
	{
		animMap .15 NewWallpaper/1.tga NewWallpaper/2.tga NewWallpaper/3.tga NewWallpaper/4.tga
		blendFunc blend
		alphagen wave sin .7 0.2 0.7 .15
		rgbGen wave sin .6 .8 0.7 .15
	}
	{
		map NewWallpaper/glow.tga
		blendfunc blend
		tcMod turb 0 0.04 0 0.3
		alphagen wave sin 0.05 0.05 0.7 .15
		tcmod stretch sin 1 .1 .5 0.25
	}
	{
		map NewWallpaper/logo.tga
		tcMod turb 0 0.0015 0 0.4
		alphagen const 0.9
		rgbGen const ( 0.2 0.2 0.2 )
		blendfunc blend
	}
}


menubacknologo
{
	nomipmaps
	{
		map NewWallpaper/Background.tga
	}
	{
		animMap .15 NewWallpaper/1.tga NewWallpaper/2.tga NewWallpaper/3.tga NewWallpaper/4.tga
		blendFunc blend
		alphagen wave sin .7 0.2 0.7 .15
		rgbGen wave sin .6 .8 0.7 .15
	}
	{
		map NewWallpaper/glow.tga
		blendfunc blend
		tcMod turb 0 0.04 0 0.3
		alphagen wave sin 0.05 0.05 0.7 .15
		tcmod stretch sin 1 .1 .5 0.25
	}
	{
		map NewWallpaper/logo.tga
		tcMod turb 0 0.0015 0 0.4
		alphagen const 0.9
		rgbGen const ( 0.2 0.2 0.2 )
		blendfunc blend
	}
}
