import itk
import numpy as np
from utils import get_image_path
from main import SCAN1_NAME, SCAN2_NAME
from tqdm import tqdm

def recalage_main(fixed_filepath=get_image_path(SCAN1_NAME), moving_filepath=get_image_path(SCAN2_NAME), verbose=False):
    fixed_image = itk.imread(fixed_filepath, itk.F)
    moving_image = itk.imread(moving_filepath, itk.F)

    fixed_array = itk.GetArrayViewFromImage(fixed_image)
    moving_array = itk.GetArrayViewFromImage(moving_image)

    nb_slices = fixed_array.shape[0]
    slices = []

    for i in tqdm(range(nb_slices), desc="Slice processing"):
        fixed_slice = fixed_array[i, :, :]
        moving_slice = moving_array[i, :, :]

        registered_slice = recalage_slice(fixed_slice, moving_slice, verbose=verbose)
        slices.append(itk.GetArrayViewFromImage(registered_slice))

    registered_array = np.stack(slices, axis=0)
    registered_image = itk.GetImageFromArray(registered_array)

    registered_image.SetSpacing(fixed_image.GetSpacing())
    registered_image.SetOrigin(fixed_image.GetOrigin())
    registered_image.SetDirection(fixed_image.GetDirection())
    return registered_image

def recalage_slice(array_fixed, array_moving, verbose=False):
    fixed_image = itk.GetImageFromArray(array_fixed)
    moving_image = itk.GetImageFromArray(array_moving)

    TransformType = itk.Rigid2DTransform[itk.D]
    initial_transform = TransformType.New()

    optimizer = itk.RegularStepGradientDescentOptimizerv4.New()
    optimizer.SetLearningRate(4.0)
    optimizer.SetMinimumStepLength(0.001)
    optimizer.SetNumberOfIterations(200)

    FixedImageType = type(fixed_image)
    MovingImageType = type(moving_image)

    metric = itk.MattesMutualInformationImageToImageMetricv4[FixedImageType, MovingImageType].New()
    metric.SetNumberOfHistogramBins(50)

    registration = itk.ImageRegistrationMethodv4.New(
        FixedImage=fixed_image,
        MovingImage=moving_image,
        Metric=metric,
        Optimizer=optimizer,
        InitialTransform=initial_transform
    )

    moving_initial_transform = TransformType.New()
    initial_parameters = moving_initial_transform.GetParameters()
    initial_parameters[0] = 0.0
    initial_parameters[1] = 0.0
    initial_parameters[2] = 0.0
    moving_initial_transform.SetParameters(initial_parameters)

    scale_parameters = moving_initial_transform.GetParameters()
    scale_parameters[0] = 1000
    scale_parameters[1] = 1
    scale_parameters[2] = 1
    optimizer.SetScales(scale_parameters)

    registration.SetMovingInitialTransform(moving_initial_transform)

    fixed_parameters = moving_initial_transform.GetFixedParameters()
    fixed_parameters[0] = moving_image.GetLargestPossibleRegion().GetSize()[0] / 2.0
    fixed_parameters[1] = moving_image.GetLargestPossibleRegion().GetSize()[1] / 2.0
    moving_initial_transform.SetFixedParameters(fixed_parameters)

    identity_transform = TransformType.New()
    identity_transform.SetIdentity()
    registration.SetFixedInitialTransform(identity_transform)
    registration.SetNumberOfLevels(1)

    registration.Update()

    transform = registration.GetTransform()
    final_parameters = transform.GetParameters()
    angle = final_parameters.GetElement(0)
    translation_x = final_parameters.GetElement(1)
    translation_y = final_parameters.GetElement(2)

    number_of_iterations = optimizer.GetCurrentIteration()
    best_value = optimizer.GetValue()

    if verbose:
        print(f"Angle: {angle}")
        print(f"Translation X: {translation_x}")
        print(f"Translation Y: {translation_y}")
        print(" Iterations    = " + str(number_of_iterations))
        print(" Metric value  = " + str(best_value))

    resampler = itk.ResampleImageFilter.New(
        Input=moving_image,
        Transform=transform,
        UseReferenceImage=True,
        ReferenceImage=fixed_image
    )
    resampler.SetDefaultPixelValue(100)
    resampler.Update()
    registered_image = resampler.GetOutput()

    if registered_image is None:
        raise ValueError("Error : 'registered_image' is None.")

    return registered_image
