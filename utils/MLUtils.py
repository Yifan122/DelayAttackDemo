import tensorflow as tf
from keras.backend.tensorflow_backend import set_session
from keras.models import load_model
from sklearn.externals import joblib



class MLObject:
    def __init__(self, model_path, x_path, y_path):
        config = tf.ConfigProto()
        set_session(tf.Session(config=config))

        self.model = load_model(model_path)
        self.scaler_X = joblib.load(x_path)
        self.scaler_y = joblib.load(y_path)

    def prediction(self, inputs):
        X = self.scaler_X.transform(inputs)

        X_shape = list(X.shape)
        X_shape[-1] = int(X_shape[-1] / 3)  # input size=3
        step = int(X_shape[-1] / 20)
        lengh = step * 20
        X = X.reshape((X_shape[0], 3, -1))[:, :, :lengh]  # here is hust want to ingnore extra data than for example 200
        X = X.reshape((X_shape[0], 20, -1))  ##number of records * seq_lengh*3*1

        predict = self.scaler_y.inverse_transform(self.model.predict(X))
        return predict



