import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import tensorflow as tf
import math


def plot_simple_timeseries_data(df_column, y_label, title):
    fig = plt.figure()
    fig.set_figheight(8)
    fig.set_figwidth(22)
    # plotting the training and validation loss
    timesteps = range(1, len(df_column) + 1)
    plt.plot(timesteps, df_column, '-,', label=y_label)
    plt.title(title)
    plt.xlabel('sample / time')
    plt.ylabel(y_label)
    plt.legend()
    plt.tight_layout(pad=4.0)
    plt.show()


def plot_simple_loss(history, title):
    fig = plt.figure()
    fig.set_figheight(5)
    fig.set_figwidth(11)

    # plotting the training and validation loss
    loss_values = history.history['loss']
    val_loss_values = history.history['val_loss']

    epochs = range(1, len(loss_values) + 1)
    plt.plot(epochs, loss_values, 'bo', label='Training Loss')
    plt.plot(epochs, val_loss_values, 'b', label='Validation Loss')
    plt.title('Training and Validation Loss:  ' + title)
    plt.xlabel('Epochs')
    plt.ylabel('Loss')
    plt.legend()

    plt.tight_layout(pad=4.0)
    plt.show()


def normalise_data(dataframe, num_training, num_validation):
    test_samples = len(dataframe) - (num_training + num_validation)

    # setting values to end sample for each
    num_validation += num_training
    test_samples += num_validation
    print(
        f"final sample - training: {num_training}th, validation: {num_validation}th, test: {test_samples}th")

    # normalising data
    mean = dataframe[:num_training].mean(axis=0)
    dataframe -= mean
    std = dataframe[:num_training].std(axis=0)
    dataframe /= std

    return dataframe


def normalisation_values(dataframe, num_training, num_validation):
    test_samples = len(dataframe) - (num_training + num_validation)

    # setting values to end sample for each
    num_validation += num_training
    test_samples += num_validation

    mean = dataframe[:num_training].mean(axis=0)
    std = dataframe[:num_training].std(axis=0)

    return mean, std


def split_dataframe(dataframe, num_training, num_validation):
    train_data = dataframe[:num_training]
    val_data = dataframe[num_training:(num_training + num_validation)]
    test_data = dataframe[(num_training + num_validation):]
    return train_data, val_data, test_data


def create_datasets(dataframe, target_column_name, num_training, num_validation, lookback, step, delay, batch_size):
    # adapted from https://keras.io/examples/timeseries/timeseries_weather_forecasting/
    target_column_num = dataframe.columns.get_loc(target_column_name)

    train_data, val_data, test_data = split_dataframe(
        dataframe, num_training, num_validation)
    # Setting up the training data
    start = lookback + delay
    end = start + num_training

    x_train = pd.DataFrame(train_data).to_numpy()
    y_train = dataframe.iloc[start:end, target_column_num]
    y_train = pd.DataFrame(y_train).to_numpy()

    # setting up the validation data
    start = end
    end = start + num_validation

    x_val = pd.DataFrame(val_data).to_numpy()
    y_val = dataframe.iloc[start:end, target_column_num]
    y_val = pd.DataFrame(y_val).to_numpy()

    # setting up test data
    start = end
    end = len(dataframe)

    x_test = pd.DataFrame(test_data).to_numpy()
    x_test = x_test[:-(lookback + delay)]
    y_test = dataframe.iloc[start:end, target_column_num]
    y_test = pd.DataFrame(y_test).to_numpy()

    # setting the sequence length - relevant when
    sequence_length = int(lookback / step)  # in case change the step later

    train_dataset = tf.keras.preprocessing.timeseries_dataset_from_array(
        x_train,
        y_train,
        sequence_length=sequence_length,
        sampling_rate=step,
        batch_size=batch_size,
    )

    val_dataset = tf.keras.preprocessing.timeseries_dataset_from_array(
        x_val,
        y_val,
        sequence_length=sequence_length,
        sampling_rate=step,
        batch_size=batch_size,
    )

    test_dataset = tf.keras.preprocessing.timeseries_dataset_from_array(
        x_test,
        y_test,
        sequence_length=sequence_length,
        sampling_rate=step,
        batch_size=batch_size,
    )

    return train_dataset, val_dataset, test_dataset


def get_dataset_shape(train_dataset):
    for batch in train_dataset.take(1):
        inputs, targets = batch
    print("Input shape:", inputs.numpy().shape)
    print("Target shape:", targets.numpy().shape)
    return inputs.shape[1], inputs.shape[2]


def plot_timeseries_features(dataframe, feature_names, time_column, feature_titles=False):
    # adapted from https://keras.io/examples/timeseries/timeseries_weather_forecasting/
    time_data = dataframe[time_column]
    fig = plt.figure(figsize=(12, 20))
    columns = 2
    rows = math.ceil(len(feature_names)/2)

    # reference https://stackoverflow.com/questions/53521396/how-to-implement-automatic-color-change-in-matplotlib-with-subplots
    colours = plt.rcParams["axes.prop_cycle"]()

    for i in range(0, len(feature_names)):
        c = next(colours)["color"]
        ax = fig.add_subplot(rows, columns, i+1)
        col_data = dataframe[feature_names[i]]
        col_data.index = time_data
        col_data.head()
        if feature_titles:
            ax = col_data.plot(c=c, rot=25, title=feature_titles[i])
        else:
            ax = col_data.plot(c=c, rot=25)
        ax.legend([feature_names[i]])
    plt.tight_layout()
    plt.show()


def print_largest_each_column(dataframe, column_names, number_largest):
    print('-' * 80)
    for i in range(0, len(column_names)):
        top = dataframe[column_names[i]].nlargest(number_largest)
        print(column_names[i])
        print(top)
        print('-' * 80)


def rows_with_nan_values(dataframe):
    # https://www.kite.com/python/answers/how-to-find-the-indices-of-rows-in-a-pandas-dataframe-containing-nan-values-in-python
    rows_with_nan = []
    for index, row in dataframe.iterrows():
        nan_indexes = row.isnull()
        if nan_indexes.any():
            rows_with_nan.append(index)
    return rows_with_nan


def plot_heatmap(dataframe, coin_name, column_names):

    # Adapted from: https://keras.io/examples/timeseries/timeseries_weather_forecasting/
    cor = dataframe.corr()
    plt.figure(figsize=(10, 10))
    plt.matshow(cor, fignum=1)
    plt.xticks(np.arange(len(column_names)),
               column_names, rotation=90, fontsize=16)
    plt.gca().xaxis.tick_bottom()
    plt.yticks(np.arange(len(column_names)), column_names, fontsize=16)
    cb = plt.colorbar()
    plt.title(coin_name + " Feature Correlation Heatmap", fontsize=20)

    plt.show()


def pred_mean_absolute_percentage_error(targets, predictions):
    absolute_errors = np.abs(targets - predictions)
    return np.mean((absolute_errors/targets))


def pred_root_mean_squared_error(targets, predictions):
    absolute_errors = np.abs(targets - predictions)
    return np.sqrt(np.mean(absolute_errors**2))


def pred_mean_squared_error(targets, predictions):
    absolute_errors = np.abs(targets - predictions)
    return np.mean(absolute_errors**2)


def lowest_val_loss_and_epoch(history):
    lowest_val_loss = -1
    lowest_epoch = 0
    for i in range(0, len(history.history['val_loss'])):
        epoch = i+1
        val_loss = history.history['val_loss'][i]
        if lowest_val_loss == -1 or val_loss < lowest_val_loss:
            lowest_val_loss = val_loss
            lowest_epoch = epoch
    return lowest_val_loss, lowest_epoch
