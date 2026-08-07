from pythonforandroid.recipe import Recipe
import os, shutil

class FFmpegRecipe(Recipe):
    version = "1.0"
    url = None

    def build_arch(self, arch):
        src = os.path.join(self.recipe_dir, arch.arch, "libffmpegbin.so")

        build_dir = self.get_build_dir(arch.arch)
        os.makedirs(build_dir, exist_ok=True)

        dst = os.path.join(build_dir, "libffmpegbin.so")
        shutil.copy2(src, dst)

    def install_libraries(self, arch):
        build_dir = self.get_build_dir(arch.arch)
        src = os.path.join(build_dir, "libffmpegbin.so")

        dst = os.path.join(self.ctx.get_libs_dir(arch.arch), "libffmpegbin.so")
        shutil.copy2(src, dst)

recipe = FFmpegRecipe()