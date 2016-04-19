import tensorflow as tf
import deepautoencoder.data


class BasicAutoEncoder:
    """A basic autoencoder with a single hidden layer. This is not to be externally used but internally by
    StackedAutoEncoder"""

    def __init__(self, data_x, data_x_, labels, hidden_dim, activation, loss, lr, print_step, epoch, batch_size=50):
        self.labels = labels
        self.print_step = print_step
        self.lr = lr
        self.loss = loss
        self.activation = activation
        self.data_x_ = data_x_
        self.data_x = data_x
        self.batch_size = batch_size
        self.epoch = epoch
        self.hidden_dim = hidden_dim
        self.input_dim = len(data_x[0])
        self.hidden_feature = []
        # self.x = None
        # self.x_ = None

    def activate(self, linear, name):
        if name == 'sigmoid':
            return tf.nn.sigmoid(linear, name='encoded')
        elif name == 'softmax':
            return tf.nn.softmax(linear, name='encoded')
        elif name == 'linear':
            return linear
        elif name == 'tanh':
            return tf.nn.tanh(linear, name='encoded')
        elif name == 'relu':
            return tf.nn.relu(linear, name='encoded')

    def cross_entropy(self, logits, output):
        return -tf.reduce_sum(output * tf.log(logits) + (1 - output) * tf.log(1 - logits))

    def train(self, x_, decoded, y):
        if self.loss == 'rmse':
            loss = tf.sqrt(tf.reduce_mean(tf.square(tf.sub(x_, decoded)))) + self.cross_entropy(
                self.activate(x_, 'softmax'), y)

        elif self.loss == 'cross-entropy':
            loss = self.cross_entropy(decoded, x_)

        train_op = tf.train.AdamOptimizer(self.lr).minimize(loss)
        return loss, train_op

    def run(self):
        sess = tf.Session()
        x = tf.placeholder(dtype=tf.float32, shape=[None, self.input_dim], name='x')
        x_ = tf.placeholder(dtype=tf.float32, shape=[None, self.input_dim], name='x_')
        y = tf.placeholder(dtype=tf.float32, shape=[None, 3], name='y')
        encode = {'weights': tf.Variable(tf.truncated_normal([self.input_dim, self.hidden_dim], dtype=tf.float32)),
                  'biases': tf.Variable(tf.truncated_normal([self.hidden_dim], dtype=tf.float32))}
        encoded_vals = tf.matmul(x, encode['weights']) + encode['biases']
        encoded = self.activate(encoded_vals, self.activation)
        decode = {'biases': tf.Variable(tf.truncated_normal([self.input_dim], dtype=tf.float32))}
        decoded = tf.matmul(encoded, tf.transpose(encode['weights'])) + decode['biases']
        loss, train_op = self.train(x_, decoded, y)
        sess.run(tf.initialize_all_variables())
        for i in range(self.epoch):
            b_x, b_x_, b_y = deepautoencoder.data.get_batch(self.data_x, self.data_x_, self.labels, self.batch_size)
            sess.run(train_op, feed_dict={x: b_x, x_: b_x_, y: b_y})
            if (i + 1) % self.print_step == 0:
                l = sess.run(loss, feed_dict={x: self.data_x, x_: self.data_x_, y: self.labels})
                print('epoch {0}: global loss = {1}'.format(i, l))

        # debug
        # print('Decoded', sess.run(decoded, feed_dict={x: self.data_x_})[0])
        return sess.run(encoded, feed_dict={x: self.data_x_}), sess.run(
            encode['weights']), sess.run(encode['biases'])
