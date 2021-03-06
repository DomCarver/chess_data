import netCDF4 as nc # importing library to read netcdf files
import numpy as np # importing numpy for dealing with multidimensional arrays
import pandas as pd # importing pandas for creating data frames
import os


class ChessDataset:
    def __init__(self, dataset_path):
        self.dataset_path = dataset_path
        self.df = None


    def extract(self, xbounds=(308000 , 322000), ybounds=(510000, 519000)):
        """this defines a function called extract_rainfall with the argument dataset_path which
        needs to be a string corresponding to the location of you input netCDF file"""

        data = nc.Dataset(self.dataset_path) # instantiate an object called data which is in the class Dataset from netCDF4

        variables = ['tas', 'precip', 'pet', 'dtr', 'rainfall_amount']
        variable_name = None
        for v in variables:
            if v in data.variables.keys():
                variable_name = v
                break
        if variable_name == 'rainfall_amount':
            ybounds = (ybounds[1], ybounds[0])
        if not variable_name:
            return "Can't find any of the specified variables"

        times = data.variables['time']
        dates = nc.num2date(times[:], times.units, times.calendar)

        x = data.variables['x'][:] # get the entire series of x values from the netCDF file
        y = data.variables['y'][:] # same for y

        # get the minimum difference between the x values in the dataset and the boundry
        xli = np.argmin(np.abs(x - xbounds[0]))
        xui = np.argmin(np.abs(x - xbounds[1])) + 1

        # same for y
        yli = np.argmin(np.abs(y - ybounds[0]))
        yui = np.argmin(np.abs(y - ybounds[1])) + 1

        # get the list of values of y and x within the boundaries
        y_select = y[yli:yui]
        x_select = x[xli:xui]

        grid = data.variables[variable_name][:, yli:yui, xli:xui] # get the 3D array within the boundaries for all time
        df = pd.DataFrame() # create a new dataframe to put the extracted series into

        for xi, x in enumerate(x_select):  # iterate over the indexes and values in the list of x coordinates

            for yi, y in enumerate(y_select): # iterate over the indexes and values in the list of y coordinates

                # Create a column name using the x and y coordinates
                column_name = '(' + str(x) + ',' + str(y) + ')'

                # Save the time series to the column
                df[column_name] = grid[:, yi, xi]

        self.df = df.set_index(dates).sort_index()

    def save_to_csv(self, filename):
        # Save to a CSV file
        self.df.to_csv(filename)


def extract_dir(directory, output_filename):
    """Get all the files in a single directory and send them to a single output file"""
    print 'extracting', directory, 'to', output_filename
    df = pd.DataFrame()
    for name in os.listdir(directory):
        if '.nc' in name:
            data = ChessDataset(os.path.join(directory, name))
            data.extract()
            df = pd.concat([df, data.df])
    df = df.sort_index()
    df.to_csv(output_filename)


def extract_all_dirs(outer_directory='/Volumes/TOSHIBA EXT'):
    """Get all the netCDF files in each directory starting with CHESS_ and send them to files in the current location"""
    names = []
    for name in os.listdir(outer_directory):
        if name.lower().startswith('chess_') or name.lower().startswith('ceh'):
            names.append(name)

    for name in names:
        extract_dir(os.path.join(outer_directory, name), name + '.csv')


def extract_file(filename, output_filename):
    """Converts a single netCDF file with any variable in the list 'tas', 'precip', 'pet', 'dtr'"""
    chess_data = ChessDataset(filename)
    chess_data.extract()
    chess_data.save_to_csv(output_filename)
