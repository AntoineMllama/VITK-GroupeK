import itk

lower = 500
upper = 1000
seedX = 120
seedY = 65


def seg(input_array, slide_index):

    slice_2d = input_array[slide_index, :, :]
    slice_image = itk.GetImageFromArray(slice_2d)

    smoother = itk.GradientAnisotropicDiffusionImageFilter.New(Input=slice_image, NumberOfIterations=20, TimeStep=0.04,
                                                               ConductanceParameter=3)
    smoother.Update()

    connected_threshold = itk.ConnectedThresholdImageFilter.New(smoother.GetOutput())
    connected_threshold.SetReplaceValue(1000)
    connected_threshold.SetLower(lower)
    connected_threshold.SetUpper(upper)

    connected_threshold.SetSeed((seedX, seedY))

    connected_threshold.Update()

    segmented_slice = itk.GetArrayViewFromImage(connected_threshold.GetOutput())
    return segmented_slice
