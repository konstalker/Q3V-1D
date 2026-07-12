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
}

levelShotDetail
{
    nomipmaps
    nopicmip
    {
        map NewWallpaper/Background.tga
        alphagen const 0.5
        blendfunc blend
    }
    {
		animMap 8 NewWallpaper/q3void/2.tga NewWallpaper/q3void/1.tga NewWallpaper/q3void/3.tga NewWallpaper/q3void/4.tga
		blendfunc blend
    }
}
