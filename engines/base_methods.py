from pathlib import Path
import urllib.request
import urllib.error
import os
import subprocess
import shlex

def check_vulkan_support() -> bool:
    """
    Честно проверяет поддержку Vulkan:
    1. Наличие системного Loader'а.
    2. Успешность создания VkInstance.
    3. Наличие хотя бы одного совместимого GPU.
    """
    instance = None
    try:
        # Минимальная спецификация приложения
        import vulkan as vk
        app_info = vk.VkApplicationInfo(
            sType=vk.VK_STRUCTURE_TYPE_APPLICATION_INFO,
            pApplicationName="VulkanCheck",
            applicationVersion=vk.VK_MAKE_VERSION(1, 0, 0),
            pEngineName="NoEngine",
            engineVersion=vk.VK_MAKE_VERSION(1, 0, 0),
            apiVersion=vk.VK_API_VERSION_1_0,
        )

        create_info = vk.VkInstanceCreateInfo(
            sType=vk.VK_STRUCTURE_TYPE_INSTANCE_CREATE_INFO,
            pApplicationInfo=app_info,
        )

        # 1. Попытка создания инстанса (упадет, если нет Vulkan Loader или драйвера)
        instance = vk.vkCreateInstance(create_info, None)

        # 2. Перечисление доступных видеокарт
        devices = vk.vkEnumeratePhysicalDevices(instance)

        return len(devices) > 0
    
        if instance is not None:
            vk.vkDestroyInstance(instance, None)

    except Exception:
        # Падает с ошибками VK_ERROR_INCOMPATIBLE_DRIVER, OSError и т.д.
        return False

def check_url(url):
    try:
        response = urllib.request.urlopen(url, timeout=5)
        return response.status == 200
    except Exception:
        return False

def caption():
    print("contacts of creator: https://telegram.me/konstalker")
    print("you can add issue on github: https://github.com/konstalker/Q3V-1D/issues")
    print("thank you for use Q3V#1D")

class C_INFO:
    def __init__(self):
        
        with open("./mod_tree/branch.txt", 'r') as f:
            self.compilation_branch, self.mod_branch, self.repo_url, self.s_data = f.read().split('\n')[:4]
        self.values = [["[OS]", self.s_data],
                       ["[CBRANCH]", self.compilation_branch],
                       ["[RURL]", self.repo_url]
                      ]

c_info = C_INFO()

def furl(url):
    for x in c_info.values:
        url = url.replace(x[0], x[1])
    return url

def get_relative_paths(folder_path: str) -> list[str]:
    base_dir = Path(folder_path)
    relative_paths = []
    
    for item in base_dir.rglob('*'):
        if item.is_file():
            rel_path = item.relative_to(base_dir)
            relative_paths.append(f"/{rel_path.as_posix()}")
            
    return relative_paths

    
def launch(args='+set fs_homepath "../baseq3/mods" +set fs_basepath "../" +set fs_game "osp" +set com_viewlog "0"', force_ogl=False):
    vk_engine, ogl_engine = None, False
    if os.path.exists('./engine.txt'):
        with open('./engine.txt') as engine_file:
            engine_conf = engine_file.read().split('\n')
            if len(engine_conf) == 2:
                vk_engine, ogl_engine = engine_conf[:2]
            else:
                vk_engine, ogl_engine = engine_conf[0], False
    else:
        return False

    has_vulkan = check_vulkan_support()

    engine = ogl_engine if (force_ogl or not c_info.s_data == 'linux' or not has_vulkan) else vk_engine

    if c_info.s_data == 'linux':
        os.system(f'chmod +x {engine}')

    subprocess.Popen([engine] + shlex.split(args))
    return True
