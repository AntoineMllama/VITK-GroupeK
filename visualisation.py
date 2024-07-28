import vtk
from vtk.util import numpy_support
import numpy as np
import segmentation
from screeninfo import get_monitors

SLICE_INDEX = 83
array1 = None
array2 = None
array1seg = None
array2seg = None
image_vtk1 = None
image_vtk2 = None
image_vtk1seg = None
image_vtk2seg = None
image_dif = None
dif = None
renderWindow = None

init = False


def update_slice(slice_index):

    global dif, init

    slice_array1 = array1[slice_index, :, :]
    slice_array2 = array2[slice_index, :, :]
    slice_array1seg = segmentation.seg(array1seg, slice_index)
    slice_array2seg = segmentation.seg(array2seg, slice_index)

    slice_array1_flipped = np.flipud(slice_array1)
    slice_array2_flipped = np.flipud(slice_array2)
    slice_array1seg_flipped = np.flipud(slice_array1seg)
    slice_array2seg_flipped = np.flipud(slice_array2seg)
    if init:
        dif = slice_array2seg_flipped - slice_array1seg_flipped
        dif[dif < 0] = 0
    init = True
    # dif_flipped = np.flipud(dif)

    slice_vtk1 = numpy_support.numpy_to_vtk(num_array=slice_array1_flipped.ravel(), deep=True, array_type=vtk.VTK_FLOAT)
    slice_vtk2 = numpy_support.numpy_to_vtk(num_array=slice_array2_flipped.ravel(), deep=True, array_type=vtk.VTK_FLOAT)
    slice_vtk1seg = numpy_support.numpy_to_vtk(num_array=slice_array1seg_flipped.ravel(), deep=True, array_type=vtk.VTK_FLOAT)
    slice_vtk2seg = numpy_support.numpy_to_vtk(num_array=slice_array2seg_flipped.ravel(), deep=True, array_type=vtk.VTK_FLOAT)
    slice_dif = numpy_support.numpy_to_vtk(num_array=dif.ravel(), deep=True, array_type=vtk.VTK_FLOAT)

    image_vtk1.SetDimensions(slice_array1_flipped.shape[1], slice_array1_flipped.shape[0], 1)
    image_vtk1.GetPointData().SetScalars(slice_vtk1)
    image_vtk2.SetDimensions(slice_array2_flipped.shape[1], slice_array2_flipped.shape[0], 1)
    image_vtk2.GetPointData().SetScalars(slice_vtk2)
    image_vtk1seg.SetDimensions(slice_array1seg_flipped.shape[1], slice_array1seg_flipped.shape[0], 1)
    image_vtk1seg.GetPointData().SetScalars(slice_vtk1seg)
    image_vtk2seg.SetDimensions(slice_array2seg_flipped.shape[1], slice_array2seg_flipped.shape[0], 1)
    image_vtk2seg.GetPointData().SetScalars(slice_vtk2seg)
    image_dif.SetDimensions(dif.shape[1], dif.shape[0], 1)
    image_dif.GetPointData().SetScalars(slice_dif)

    renderWindow.Render()


def slider_callback(obj, event):
    slider_value = int(obj.GetRepresentation().GetValue())
    update_slice(slider_value)


def run_visual(array1in, array2in, arrayseg1in, arrayseg2in):
    global array1, array2, array1seg, array2seg, image_vtk1, image_vtk2, image_vtk1seg, image_vtk2seg, dif, image_dif, renderWindow
    array1 = array1in
    array2 = array2in
    array1seg = arrayseg1in
    array2seg = arrayseg2in
    dif = np.zeros((array1.shape[1], array1.shape[2]))
    image_vtk1 = vtk.vtkImageData()
    image_vtk2 = vtk.vtkImageData()
    image_vtk1seg = vtk.vtkImageData()
    image_vtk2seg = vtk.vtkImageData()
    image_dif = vtk.vtkImageData()

    mapper1 = vtk.vtkImageMapper()
    mapper1.SetInputData(image_vtk1)
    mapper2 = vtk.vtkImageMapper()
    mapper2.SetInputData(image_vtk2)
    mapper1seg = vtk.vtkImageMapper()
    mapper1seg.SetInputData(image_vtk1seg)
    mapper2seg = vtk.vtkImageMapper()
    mapper2seg.SetInputData(image_vtk2seg)
    mapperdif = vtk.vtkImageMapper()
    mapperdif.SetInputData(image_dif)

    actor1 = vtk.vtkActor2D()
    actor1.SetMapper(mapper1)
    actor2 = vtk.vtkActor2D()
    actor2.SetMapper(mapper2)
    actor1seg = vtk.vtkActor2D()
    actor1seg.SetMapper(mapper1seg)
    actor2seg = vtk.vtkActor2D()
    actor2seg.SetMapper(mapper2seg)
    actordif = vtk.vtkActor2D()
    actordif.SetMapper(mapperdif)

    monitor = get_monitors()[0]
    screen_width = monitor.width
    screen_height = monitor.height
    window_width = int(screen_width)
    window_height = int(screen_height)

    renderer = vtk.vtkRenderer()
    renderWindow = vtk.vtkRenderWindow()
    renderWindow.AddRenderer(renderer)
    renderWindow.SetSize(window_width, window_height)
    renderWindow.SetPosition(int((screen_width - window_width) / 2), int((screen_height - window_height) / 2))
    renderWindowInteractor = vtk.vtkRenderWindowInteractor()
    renderWindowInteractor.SetRenderWindow(renderWindow)

    renderer.AddActor(actor1)
    renderer.AddActor(actor2)
    renderer.AddActor(actor1seg)
    renderer.AddActor(actor2seg)
    renderer.AddActor(actordif)
    renderer.SetBackground(1, 1, 1)

    actor1.SetPosition((renderWindow.GetSize()[0] // 2) - array1.shape[1], renderWindow.GetSize()[1] // 2)
    actor2.SetPosition((renderWindow.GetSize()[0] // 2), renderWindow.GetSize()[1] // 2)
    actor1seg.SetPosition((renderWindow.GetSize()[0] // 2) - array1seg.shape[1], renderWindow.GetSize()[1] // 2 - (array1seg.shape[2]))
    actor2seg.SetPosition((renderWindow.GetSize()[0] // 2), renderWindow.GetSize()[1] // 2 - array2seg.shape[2])
    actordif.SetPosition(renderWindow.GetSize()[0] // 2 + (2 * dif.shape[1]), renderWindow.GetSize()[1] // 2 - (array1seg.shape[2] // 2))

    textActor1 = vtk.vtkTextActor()
    textActor1.SetInput("Image 1 Brut")
    textActor1.SetPosition((renderWindow.GetSize()[0] // 2) - array1.shape[1], (renderWindow.GetSize()[1] // 2) + array1.shape[2])
    textActor1.GetTextProperty().SetFontSize(24)
    textActor1.GetTextProperty().SetColor(1, 0, 0)

    textActor2 = vtk.vtkTextActor()
    textActor2.SetInput("Image 2 Brut")
    textActor2.SetPosition((renderWindow.GetSize()[0] // 2) + array2.shape[1] // 2, (renderWindow.GetSize()[1] // 2) + array2.shape[2])
    textActor2.GetTextProperty().SetFontSize(24)
    textActor2.GetTextProperty().SetColor(1, 0, 0)

    textActor1seg = vtk.vtkTextActor()
    textActor1seg.SetInput("Image 1 Segment")
    textActor1seg.SetPosition((renderWindow.GetSize()[0] // 2) - array1seg.shape[1], (renderWindow.GetSize()[1] // 2) - array1seg.shape[2] - 24)
    textActor1seg.GetTextProperty().SetFontSize(24)
    textActor1seg.GetTextProperty().SetColor(1, 0, 0)

    textActor2seg = vtk.vtkTextActor()
    textActor2seg.SetInput("Image 2 Segment")
    textActor2seg.SetPosition((renderWindow.GetSize()[0] // 2) + array2seg.shape[1] // 2, (renderWindow.GetSize()[1] // 2) - array2seg.shape[2] - 24)
    textActor2seg.GetTextProperty().SetFontSize(24)
    textActor2seg.GetTextProperty().SetColor(1, 0, 0)

    textActordif = vtk.vtkTextActor()
    textActordif.SetInput("Difference tumeur")
    textActordif.SetPosition(renderWindow.GetSize()[0] // 2 + (2 * dif.shape[1]), renderWindow.GetSize()[1] // 2 - (array1seg.shape[2] // 2) - 24)
    textActordif.GetTextProperty().SetFontSize(24)
    textActordif.GetTextProperty().SetColor(1, 0, 0)

    renderer.AddActor2D(textActor1)
    renderer.AddActor2D(textActor2)
    renderer.AddActor2D(textActor1seg)
    renderer.AddActor2D(textActor2seg)
    renderer.AddActor2D(textActordif)

    sliderRep = vtk.vtkSliderRepresentation2D()
    sliderRep.SetMinimumValue(0)
    sliderRep.SetMaximumValue(array1.shape[0] - 1)
    sliderRep.SetValue(SLICE_INDEX)
    sliderRep.SetTitleText("Slice Index")
    sliderRep.GetSliderProperty().SetColor(1, 0, 0)
    sliderRep.GetTitleProperty().SetColor(1, 0, 0)
    sliderRep.GetLabelProperty().SetColor(1, 0, 0)
    sliderRep.GetSelectedProperty().SetColor(0, 1, 0)
    sliderRep.GetTubeProperty().SetColor(1, 1, 0)
    sliderRep.GetCapProperty().SetColor(1, 1, 0)
    sliderRep.SetSliderLength(0.02)
    sliderRep.SetSliderWidth(0.03)
    sliderRep.SetEndCapLength(0.01)
    sliderRep.SetEndCapWidth(0.03)
    sliderRep.SetTubeWidth(0.005)
    sliderRep.SetTitleHeight(0.02)
    sliderRep.SetLabelHeight(0.02)
    sliderRep.GetPoint1Coordinate().SetCoordinateSystemToDisplay()
    sliderRep.GetPoint1Coordinate().SetValue((renderWindow.GetSize()[0] // 2) - array1.shape[1], renderWindow.GetSize()[1] - (array1.shape[2] // 2))
    sliderRep.GetPoint2Coordinate().SetCoordinateSystemToDisplay()
    sliderRep.GetPoint2Coordinate().SetValue((renderWindow.GetSize()[0] // 2) + array2.shape[1], renderWindow.GetSize()[1] - (array2.shape[2] // 2))

    sliderWidget = vtk.vtkSliderWidget()
    sliderWidget.SetInteractor(renderWindowInteractor)
    sliderWidget.SetRepresentation(sliderRep)
    sliderWidget.SetAnimationModeToAnimate()

    sliderWidget.AddObserver("EndInteractionEvent", slider_callback)
    sliderWidget.EnabledOn()
    update_slice(SLICE_INDEX)

    renderWindow.Render()
    renderWindowInteractor.Start()
