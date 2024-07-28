import recalage
import visualisation
import recalage
import utils

SCAN1_NAME = 'case6_gre1.nrrd'
SCAN2_NAME = 'case6_gre2.nrrd'

if __name__ == '__main__':
    image1 = utils.get_image(SCAN1_NAME)
    array1 = utils.image_to_array(image1)

    recaled = recalage.recalage_main()
    array2 = utils.image_to_array(recaled)

    visualisation.run_visual(array1, array2, array1, array2)