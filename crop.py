import cv2
import os
import argparse
from tqdm import tqdm
import glob

ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image", help="path to the images")
ap.add_argument("-s", "--skipimage", help="If True, crop images for one in five picture else crop all images", default=False)
args = ap.parse_args()


class CropImage:
    output_folder_name = "cropped_images"
    h_start_end_crop_percent = 0.1
    per_image = 5
    w_start_end_crop_percent = 0.05

    def __init__(self, image_path: str, skip_image: bool):
        self.image_path = image_path
        self.skip_image = skip_image

    def list_dir_path(self):
        list_dir = glob.glob(os.path.join(self.image_path, "*.png"))
        list_dir = [os.path.basename(image_name) for image_name in list_dir]
        list_dir.sort()
        return list_dir

    def iter_img(self):
        list_dir = CropImage.list_dir_path(self)
        if self.skip_image:
            new_list_dir = [img for index, img in enumerate(list_dir, start=1) if index % CropImage.per_image == 0]
            return new_list_dir
        else:
            return list_dir

    def height_pixels(self, height, size):
        if size == "4k":
            k = 1
        else:
            k = 2.166

        new_min_y = height * self.h_start_end_crop_percent * k
        new_max_y = height - new_min_y * 2
        return int(new_max_y), int(new_min_y)

    def width_pixel(self, width, size):
        width_list: list = []
        if size == "4k":
            image_count = 2
        if size == "8k":
            image_count = 4

        start_w = int(self.w_start_end_crop_percent * width)
        end_w = width - start_w * 2
        size_w = end_w - start_w
        for index in range(image_count):
            a = int(size_w / image_count)
            a += start_w
            width_list.append([start_w, a])
            start_w = a
        return width_list

    def crop_and_save(self):
        abs_path = os.path.abspath(os.path.join(self.image_path, os.pardir))

        if not os.path.exists(abs_path + "/" + self.output_folder_name):
            os.makedirs(abs_path + "/" + self.output_folder_name)

        out_folder_path = os.path.join(abs_path, self.output_folder_name)

        for image in tqdm(CropImage.iter_img(self)):
            img = cv2.imread(os.path.join(self.image_path, image))
            size = CropImage.define_pixel_size(img.shape[1])
            img_ = img.copy()
            for index, width in enumerate(CropImage.width_pixel(self, width=img.shape[1], size=size)):
                img_name_split = image.split(".")
                img_name = img_name_split[0] + "_" + str(index) + "." + img_name_split[1]
                max_h, min_h = CropImage.height_pixels(self, height=img.shape[0], size=size)
                img_ = img[min_h:max_h, width[0]:width[1], :]
                cv2.imwrite(os.path.join(out_folder_path, img_name), img_)

    @staticmethod
    def define_pixel_size(shape):
        if 3000 <= shape < 5000:
            return "4k"
        if 7000 < shape < 9000:
            return "8k"
        else:
            import logging
            log = logging.getLogger()
            log.error("This images are not 8k or 4k please check your data!")


def string2bool(arg):
    string_arg = str(arg).upper()
    if 'TRUE'.startswith(string_arg):
        return True
    elif 'FALSE'.startswith(string_arg):
        return False


CropImage(image_path=args.image, skip_image=string2bool(args.skipimage)).crop_and_save()
