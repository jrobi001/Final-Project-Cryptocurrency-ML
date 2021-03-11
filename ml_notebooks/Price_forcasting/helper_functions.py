import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import tensorflow as tf


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
    # setting witdth to 2x, so that figures can be side by side
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
    num_training = 12000
    num_validation = 7000
    test_samples = len(dataframe) - (num_training + num_validation)  # 5936

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


def split_dataframe(dataframe, num_training, num_validation):
    train_data = dataframe[:num_training]
    val_data = dataframe[num_training:(num_training + num_validation)]
    test_data = dataframe[(num_training + num_validation):]
    return train_data, val_data, test_data


def create_datasets(dataframe, target_column_num, num_training, num_validation, lookback, step, delay, batch_size):
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
