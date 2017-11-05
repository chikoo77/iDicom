import os
import vtk
from PyQt4 import QtGui, QtCore
from iDicom_ui import Ui_Form
import SimpleITK as sitk


try:
    from lib import StudyData as StudyData
    from lib import VisuAnalysisWidget
except(ImportError):
    class VisuAnalysisWidget(QtGui.QWidget):
        pass


class iDicom(VisuAnalysisWidget):

    def __init__(self, parent = None):

        self.reader = vtk.vtkDICOMImageReader()
        self.dataExtent = []
        self.dataDimensions = []
        self.dataRange = ()

        # initialize GUI
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        self.ui.WindowCenterSlider.setRange(0, 1000)
        self.ui.WindowWidthSlider.setRange(0, 1000)

        # define viewers
        [self.viewerXY, self.viewerYZ, self.viewerXZ] = [vtk.vtkImageViewer2() for x in range(3)]

        # attach interactors to viewers
        self.viewerXY.SetupInteractor(self.ui.XYPlaneWidget)
        self.viewerYZ.SetupInteractor(self.ui.YZPlaneWidget)
        self.viewerXZ.SetupInteractor(self.ui.XZPlaneWidget)

        # set render windows for viewers
        self.viewerXY.SetRenderWindow(self.ui.XYPlaneWidget.GetRenderWindow())
        self.viewerYZ.SetRenderWindow(self.ui.YZPlaneWidget.GetRenderWindow())
        self.viewerXZ.SetRenderWindow(self.ui.XZPlaneWidget.GetRenderWindow())

        # set slicing orientation for viewers
        self.viewerXY.SetSliceOrientationToXZ()
        self.viewerYZ.SetSliceOrientationToYZ()
        self.viewerXZ.SetSliceOrientationToXY()

        # rotate image
        act = self.viewerYZ.GetImageActor()
        act.SetOrientation(90, 0, 0)

        # setup volume rendering
        self.volRender = vtk.vtkRenderer()
        self.volRenWin = self.ui.VolumeWidget.GetRenderWindow()
        self.volRenWin.AddRenderer(self.volRender)

        self.rayCastFunction = vtk.vtkVolumeRayCastCompositeFunction()
        self.volumeMapper = vtk.vtkVolumeRayCastMapper()
        self.volumeMapper.SetVolumeRayCastFunction(self.rayCastFunction)

        volumeColor = vtk.vtkColorTransferFunction()
        volumeColor.AddRGBPoint(0,    0.0, 0.0, 0.0)
        volumeColor.AddRGBPoint(500,  1.0, 0.5, 0.3)
        volumeColor.AddRGBPoint(1000, 1.0, 0.5, 0.3)
        volumeColor.AddRGBPoint(1150, 1.0, 1.0, 0.9)
        self.volumeColor = volumeColor

        volumeScalarOpacity = vtk.vtkPiecewiseFunction()
        volumeScalarOpacity.AddPoint(0,    0.00)
        volumeScalarOpacity.AddPoint(50,  0.15)
        volumeScalarOpacity.AddPoint(100, 0.15)
        volumeScalarOpacity.AddPoint(115, 0.85)
        self.volumeScalarOpacity = volumeScalarOpacity

        volumeGradientOpacity = vtk.vtkPiecewiseFunction()
        volumeGradientOpacity.AddPoint(0,   0.0)
        volumeGradientOpacity.AddPoint(100,  0.5)
        volumeGradientOpacity.AddPoint(500, 1)
        self.volumeGradientOpacity = volumeGradientOpacity

        volumeProperty = vtk.vtkVolumeProperty()
        volumeProperty.SetColor(volumeColor)
        volumeProperty.SetScalarOpacity(volumeScalarOpacity)
        volumeProperty.SetGradientOpacity(volumeGradientOpacity)
        volumeProperty.SetInterpolationTypeToLinear()
        volumeProperty.ShadeOn()
        volumeProperty.SetAmbient(0.4)
        volumeProperty.SetDiffuse(0.6)
        volumeProperty.SetSpecular(0.2)
        self.volumeProperty = volumeProperty

        volume = vtk.vtkVolume()
        volume.SetMapper(self.volumeMapper)
        volume.SetProperty(self.volumeProperty)
        self.volume = volume

        self.volRender.AddViewProp(volume)



    def updateData(self, studydata):
        self.load_study_from_path(studydata.getPath())
        
        
    def DicomValues(self, studyPath):
        img = sitk.ReadImage(studyPath[0])
        tags_to_print = {'0010|0010': 'Patient name: ', 
                     '0008|0060' : 'Modality: ',
                     '0008|0021' : 'Series date: ',
                     '0008|0080' : 'Institution name: ',
                     '0008|1050' : 'Performing physician\'s name: ',
                     '0008|0030' : 'Series Time: ',
                     '0008|0070' : 'Manufacturer: ',
                     '0008|1090' : 'Manufacturer\'s Model Name: ',
                     '0008|1030' : 'Study Description: ',
                     '0010|0020' : 'Patient\'s ID: ',
                     '0018|0050' : 'Slice Thickness: ',
                     '0028|0010' : 'Rows: ',
                     '0028|0011' : 'Columns: ',
                     '0028|0100' : 'Bits Allocated: '}
        for tag in tags_to_print:
            try:
                print(tags_to_print[tag] + img.GetMetaData(tag))
            except:
                pass


    def load_study_from_path(self, studyPath):

        # Update reader
        self.reader.SetDirectoryName(studyPath)
        self.reader.SetDataScalarTypeToUnsignedShort()
        self.reader.UpdateWholeExtent()
        self.reader.Update()
        
        self.metaData = sitk.ImageSeriesReader()
        
    

        self.xyMapper = vtk.vtk

        # Get data dimensionality
        self.dataExtent = self.reader.GetDataExtent()
        dataDimensionX = self.dataExtent[1]-self.dataExtent[0]
        dataDimensionY = self.dataExtent[3]-self.dataExtent[2]
        dataDimensionZ = self.dataExtent[5]-self.dataExtent[4]
        self.dataDimensions = [dataDimensionX, dataDimensionY, dataDimensionZ]

        # Calculate index of middle slice
        midslice1 = int((self.dataExtent[1]-self.dataExtent[0])/2 + self.dataExtent[0])
        midslice2 = int((self.dataExtent[3]-self.dataExtent[2])/2 + self.dataExtent[2])
        midslice3 = int((self.dataExtent[5]-self.dataExtent[4])/2 + self.dataExtent[4])

        # Calculate enter
        center = [midslice1, midslice2, midslice3]

        # Get data range
        self.dataRange = self.reader.GetOutput().GetPointData().GetArray("DICOMImage").GetRange()
        print(self.dataRange)

        # Set current slice to the middle one
        for pair in zip([self.viewerXY, self.viewerYZ, self.viewerXZ], [midslice1, midslice2, midslice3]):
            pair[0].SetInputData(self.reader.GetOutput())
            pair[0].SetSlice(pair[1])
            pair[0].Render()
        pass

        # Set range and proper value for slice sliders
        for pair in zip([self.ui.XYSlider, self.ui.YZSlider, self.ui.XZSlider,], self.dataDimensions, [midslice1, midslice2, midslice3]):
            pair[0].setRange(0, pair[1])
            pair[0].setValue(pair[2])

        # Set range and value for windowing sliders
        self.ui.WindowCenterSlider.setRange(int(self.dataRange[0]), int(self.dataRange[1]))
        self.ui.WindowWidthSlider.setRange(1, int(self.dataRange[1]))

        # set input for volume renderer
        self.volumeMapper.SetInputConnection(self.reader.GetOutputPort())
        self.volRenWin.Render()
        
        self.dataReader = sitk.ImageSeriesReader()
        self.images = self.dataReader.GetGDCMSeriesFileNames(studyPath)
        self.DicomValues(self.images)
        


    # setup slots for slicing sliders
    @QtCore.pyqtSlot(int)
    def on_XYSlider_valueChanged(self, value):
        self.viewerXY.SetSlice(value)

    @QtCore.pyqtSlot(int)
    def on_YZSlider_valueChanged(self, value):
        self.viewerYZ.SetSlice(value)

    @QtCore.pyqtSlot(int)
    def on_XZSlider_valueChanged(self, value):
        self.viewerXZ.SetSlice(value)


    # Setup slots for windowing sliders
    @QtCore.pyqtSlot(int)
    def on_WindowCenterSlider_valueChanged(self, value):
        for x in [self.viewerXY, self.viewerXZ, self.viewerYZ]:
            x.SetColorLevel(value)
            x.Render()

    @QtCore.pyqtSlot(int)
    def on_WindowWidthSlider_valueChanged(self, value):
        for x in [self.viewerXY, self.viewerXZ, self.viewerYZ]:
            x.SetColorWindow(value)
            x.Render()


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    window = iDicom()
    print(type(window))
    window.show()

    dir_path = os.path.dirname(os.path.realpath(__file__))
    studyPath = str(os.path.join(dir_path, 'images'))
    window.load_study_from_path(studyPath)
    exitStatus = app.exec_()
    #del(window)
    sys.exit(exitStatus)
