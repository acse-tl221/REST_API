""" Module containing a class to process tidal data."""

import pandas as pd
#add import
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
matplotlib.use('Agg')
class Reader:
    """
    Class to process tidal data.

    data : pandas.DataFrame
        The underlying tide data.
    """

    def __init__(self, filename):
        """Read in the rainfall data from a named ``.csv``
           file using ``pandas``.

        The DataFrame data is stored in a class instance variable ``data``
        indexed by entry.

        Parameters
        ----------

        filename: str
            The file to be read

        Examples
        --------

        >>> Reader("tidalReadings.csv").data.loc[0].stationName
        'Bangor'
        """

        data=pd.read_csv(filename)
        self.data = data

    def station_tides(self, station_name, time_from=None, time_to=None):
        """Return the tide data at a named station as an ordered pandas Series,
         indexed by the dateTime data.

        Parameters
        ----------

        station_name: str or list of strs
            Station Name(s) to return
        time_from: str or None
            Time from which to report (ISO 8601 format)
        time_to: str or None
            Time up to which to report (ISO 8601 format)

        Returns
        -------

        pandas.DataFrame
            The relevant tide data indexed by dateTime and with columns the stationName(s)

        Examples
        --------

        >>> reader = Reader("tideReadings.csv")
        >>> tides = reader.station_tides(["Newlyn", "Bangor"])
        >>> tides.loc["2021-09-20T02:00:00Z", "Newlyn"]
        0.937

        """

        tide_data=self.data
        if(isinstance(station_name,str)):
            station_name=[station_name]
        valid_name=tide_data.stationName.unique()
        for name_iter in station_name:
            if name_iter not in valid_name:
                raise ValueError("invaid station name")
        df=tide_data.loc[tide_data.stationName.isin(station_name)]
        df2_column=[]
        df2_column.extend(df.stationName.unique().tolist())  # new column
        df2_index = df.dateTime.unique()  # new index
        df2=pd.DataFrame(index=df2_index, columns=df2_column)
        for row in df.itertuples():
            df2.loc[row.dateTime][row.stationName] = row.tideValue
        if (time_from or time_to):
            if ((not time_to) and time_from):
                df2=df2.loc[df2.index>=time_from]
            elif ((not time_from) and time_to):
                df2=df2.loc[df2.index<=time_to]
            elif (time_from and time_to):
                df2=df2.loc[(df2.index>=time_from)&(df2.index<=time_to)]
            return df2
        else:
            return df2

    def judege_func(self,x):
        try:
            float(x)
            return True
        except ValueError:
            return False

    def max_tides(self, time_from=None, time_to=None):
        """Return the high tide data as an ordered pandas Series,
         indexed by station name data.

        Parameters
        ----------

        time_from: str or None
            Time from which to report (ISO 8601 format).
            If ``None``, then earliest value used.
        time_to: str or None
            Time up to which to report (ISO 8601 format)
            If ``None``, then latest value used.

        Returns
        -------

        pandas.Series
            The relevant tide data indexed by stationName.

        Examples
        --------

        >>> reader = Reader("tideReadings.csv")
        >>> tides = reader.max_tides()
        >>> tides["Newlyn"]
        2.376
        """
        tide_data=self.data
        index_dirty_number=[]
        tidevalue_column=tide_data.tideValue.tolist()
        for i in range(len(tidevalue_column)):
            if self.judege_func(tidevalue_column[i]):
                continue
            else:
                index_dirty_number.append(i)
        for index_ in index_dirty_number:
            tide_data.loc[index_]['tideValue']="NaN"
        tide_data=tide_data.astype({"tideValue":float})
        if (time_from or time_to):
            if ((not time_to) and time_from):
                tide_data=tide_data.loc[tide_data.dateTime>=time_from]
            elif ((not time_from) and time_to):
                tide_data=tide_data.loc[tide_data.dateTime<=time_to]
            elif (time_from and time_to):
                tide_data=tide_data.loc[(tide_data.dateTime>=time_from)&(tide_data.dateTime<=time_to)]
        df=tide_data.groupby('stationName').tideValue.max()
        #print(df)
        return df
    
    def min_tides(self, time_from=None, time_to=None):
        """Return the low tide data as an ordered pandas Series,
         indexed by station name data.

        Parameters
        ----------

        time_from: str or None
            Time from which to report (ISO 8601 format)
            If ``None``, then earliest value used.
        time_to: str or None
            Time up to which to report (ISO 8601 format)
            If ``None``, then latest value used.

        Returns
        -------

        pandas.Series
            The relevant tide data indexed by stationName.

        Examples
        --------

        >>> reader = Reader("tideReadings.csv")
        >>> tides = reader.min_tides()
        >>> tides["Newlyn"]
        -2.231
        """
        tide_data=self.data
        index_dirty_number=[]
        tidevalue_column=tide_data.tideValue.tolist()
        for i in range(len(tidevalue_column)):
            if self.judege_func(tidevalue_column[i]):
                continue
            else:
                index_dirty_number.append(i)
        for index_ in index_dirty_number:
            tide_data.loc[index_]['tideValue']="NaN"
        tide_data=tide_data.astype({"tideValue":float})
        if (time_from or time_to):
            if ((not time_to) and time_from):
                tide_data=tide_data.loc[tide_data.dateTime>=time_from]
            elif ((not time_from) and time_to):
                tide_data=tide_data.loc[tide_data.dateTime<=time_to]
            elif (time_from and time_to):
                tide_data=tide_data.loc[(tide_data.dateTime>=time_from)&(tide_data.dateTime<=time_to)]
        df=tide_data.groupby('stationName').tideValue.min()
        return df

    def mean_tides(self, time_from=None, time_to=None):
        """Return the mean tide data as an ordered pandas Series,
         indexed by station name data.

        Parameters
        ----------

        time_from: str or None
            Time from which to report (ISO 8601 format)
        time_to: str or None
            Time up to which to report (ISO 8601 format)

        Returns
        -------

        pandas.Series
            The relevant tide data indexed by stationName.

        Examples
        --------

        >>> reader = Reader("tideReadings.csv")
        >>> tides = reader.mean_tides()
        >>> tides["Newlyn"]
        0.19242285714285723
        """
        tide_data=self.data
        index_dirty_number=[]
        tidevalue_column=tide_data.tideValue.tolist()
        for i in range(len(tidevalue_column)):
            if self.judege_func(tidevalue_column[i]):
                continue
            else:
                index_dirty_number.append(i)
        for index_ in index_dirty_number:
            tide_data.loc[index_]['tideValue']="NaN"
        tide_data=tide_data.astype({"tideValue":float})
        if (time_from or time_to):
            if ((not time_to) and time_from):
                tide_data=tide_data.loc[tide_data.dateTime>=time_from]
            elif ((not time_from) and time_to):
                tide_data=tide_data.loc[tide_data.dateTime<=time_to]
            elif (time_from and time_to):
                tide_data=tide_data.loc[(tide_data.dateTime>=time_from)&(tide_data.dateTime<=time_to)]
        df=tide_data.groupby('stationName').tideValue.mean()
        return df

    def station_graph(self, station_name, time_from=None, time_to=None):
        """Return a matplotlib graph of the tide data at a named station,
        indexed by the dateTime data.

        Parameters
        ----------

        station_name: str
            Station Name
        time_from: str or None
            Time from which to report (ISO 8601 format)
        time_to: str or None
            Time up to which to report (ISO 8601 format)

        Returns
        -------

        matplotlib.figure.Figure
            Labelled graph of station tide data.
        """
        tide_data=self.data
        index_dirty_number=[]
        valid_name=tide_data.stationName.unique()
        if station_name not in valid_name:
                raise ValueError("invaid station name")
        station_data=self.station_tides(station_name,time_from,time_to)
        station_data=station_data.astype({station_name:float})
        date_X=pd.to_datetime(station_data.index)
        X_lable=date_X.values
        Y_lable=station_data[station_name].values
        fig = plt.figure()
        plt.plot(X_lable,Y_lable,'o--g', label=station_name)
        plt.legend()
        return fig

    def add_data(self, date_time, station_name, tide_value):
        """Add data to the reader DataFrame.

        Parameters
        ----------
        date_time: str
            Time of reading in ISO 8601 format
        station_name: str
            Station Name
        time_value: float
            Observed tide in m

        Examples
        --------

        >>> reader = Reader("tideReadings.csv")
        >>> original_len = len(reader.data.index)
        >>> reader.add_data("2021-09-20T02:00:00Z",
                            "Newlyn", 1.465)
        >>> len(reader.data.index) = original_len + 1
        True
        """
        tide_data=self.data
        df_append=pd.DataFrame({"dateTime":[date_time],"stationName":[station_name],"tideValue":[tide_value]})
        tide_data=tide_data.append(df_append,ignore_index=True)
        self.data=tide_data
        return NotImplemented

    def write_data(self, filename):
        """Write data to disk in .csv format.

        Parameters
        ----------

        filename: str
            filename to write to.
        """
        tide_data=self.data
        tide_data.to_csv(filename)
        return NotImplemented


if __name__ == "__main__":
    reader = Reader("tideReadings.csv")
    try:
        print(len(reader.data.index))
    except TypeError:
        print("No data loaded.")

    #test1
    print(Reader("tideReadings.csv").data.loc[0].stationName)

    #test2
    reader = Reader("tideReadings.csv")
    tides = reader.station_tides(["Newlyn","Bangor"],time_to="2021-09-20T05:15:00Z")
    print(tides.loc["2021-09-20T02:00:00Z", "Newlyn"])

    #test3
    reader = Reader("tideReadings.csv")
    tides = reader.max_tides()
    print(tides["Newlyn"])

    #test4
    reader = Reader("tideReadings.csv")
    tides = reader.min_tides()
    print(tides["Newlyn"])

    #test5
    reader = Reader("tideReadings.csv")
    tides = reader.mean_tides()
    print(tides["Newlyn"])

    #test6
    reader = Reader("tideReadings.csv")
    tides = reader.station_graph("Newlyn",time_to="2021-09-20T05:15:00Z")

    #test7
    reader = Reader("tideReadings.csv")
    original_len = len(reader.data.index)
    reader.add_data("2021-09-20T02:00:00Z",
                            "Newlyn", 1.465)
    print(len(reader.data.index) == original_len + 1)

    reader.write_data("try.csv")
