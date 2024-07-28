import os
import itk
import matplotlib.pyplot as plt

def get_image_path(scan_name):
    path = os.path.join(os.getcwd(), 'Data', scan_name)
    return path

def get_image(scan_name):
    path = get_image_path(scan_name)
    ImageType = itk.Image[itk.F, 3]
    reader = itk.ImageFileReader[ImageType].New()
    reader.SetFileName(path)
    reader.Update()
    image = reader.GetOutput()
    return image


def display_slice(array1, array2, slice_index=0, description=""):
    if array1.shape != array2.shape:
        raise ValueError("Arrays must have the same shape")

    fig, axes = plt.subplots(1, 2, figsize=(10, 5))
    axes[0].imshow(array1, cmap='gray')
    axes[0].set_title('Image 1 - Slice ' + str(slice_index))
    axes[1].imshow(array2, cmap='gray')
    axes[1].set_title(f"Image 2 {description} - Slice {str(slice_index)}")
    plt.show()

def display_images_slice_by_slice(image1, image2, slice_index=0, nb_to_display=1):
    array1 = itk.array_from_image(image1)
    array2 = itk.array_from_image(image2)
    for i in range(nb_to_display):
        display_slice(array1[slice_index + i, :, :], array2[slice_index + i, :, :], slice_index + i)

def image_to_array(image):
    return itk.GetArrayViewFromImage(image)