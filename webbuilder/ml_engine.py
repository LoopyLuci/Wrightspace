"""webbuilder.ml_engine — auto-generated implementation."""

from __future__ import annotations

class BatchNorm:
    """BatchNorm layer."""

    def __init__(self, num_features, momentum=0.9, eps=1e-5):

        import numpy as np

        self.num_features = num_features

        self.momentum = momentum

        self.eps = eps

        self.gamma = np.ones(num_features)

        self.beta = np.zeros(num_features)

        self.running_mean = np.zeros(num_features)

        self.running_var = np.ones(num_features)

        self._input = None

        self._norm = None

        self._mean = None

        self._var = None

    def forward(self, x, training=True):

        self._input = x

        if training:

            self._mean = np.mean(x, axis=0)

            self._var = np.var(x, axis=0) + self.eps

            self.running_mean = self.momentum * self.running_mean + (1 - self.momentum) * self._mean

            self.running_var = self.momentum * self.running_var + (1 - self.momentum) * self._var

        else:

            self._mean = self.running_mean

            self._var = self.running_var

        self._norm = (x - self._mean) / np.sqrt(self._var)

        out = self.gamma * self._norm + self.beta

        return out

    def backward(self, grad):

        N = self._input.shape[0]

        dnorm = grad * self.gamma

        dvar = np.sum(dnorm * (self._input - self._mean) * (-0.5) * (self._var ** (-3/2)), axis=0)

        dmean = np.sum(dnorm * (-1 / np.sqrt(self._var)), axis=0) + dvar * np.mean(-2 * (self._input - self._mean), axis=0)

        dx = dnorm / np.sqrt(self._var) + dvar * 2 * (self._input - self._mean) / N + dmean / N

        self.grads = {'gamma': np.sum(grad * self._norm, axis=0), 'beta': np.sum(grad, axis=0)}

        return dx

    def set_learning_phase(self, training):

        pass

    pass

class Conv2D:
    """Conv2D layer."""

    def __init__(self, in_channels, out_channels, kernel_size, stride=1, padding=0):

        import numpy as np

        self.in_channels = in_channels

        self.out_channels = out_channels

        self.kernel_size = kernel_size

        self.stride = stride

        self.padding = padding

        scale = np.sqrt(2.0 / (in_channels * kernel_size * kernel_size))

        self.params = {'W': np.random.randn(out_channels, in_channels, kernel_size, kernel_size) * scale, 'b': np.zeros(out_channels)}

        self.grads = {'W': np.zeros_like(self.params['W']), 'b': np.zeros_like(self.params['b'])}

        self._input = None

        self._col = None

        self._col_W = None

    def forward(self, x):

        import numpy as np

        self._input = x

        N, C, H, W = x.shape

        K = self.kernel_size

        S = self.stride

        P = self.padding

        out_h = (H + 2*P - K) // S + 1

        out_w = (W + 2*P - K) // S + 1

        if P > 0:

            x = np.pad(x, ((0,0),(0,0),(P,P),(P,P)), mode='constant')

        self._col = np.zeros((N, C, K, K, out_h, out_w))

        for y in range(K):

            for x_ in range(K):

                self._col[:, :, y, x_, :, :] = x[:, :, y:y+out_h*S:S, x_:x_+out_w*S:S]

        self._col = self._col.transpose(0, 4, 5, 1, 2, 3).reshape(N*out_h*out_w, -1)

        self._col_W = self.params['W'].reshape(self.out_channels, -1).T

        out = self._col @ self._col_W + self.params['b']

        out = out.reshape(N, out_h, out_w, self.out_channels).transpose(0, 3, 1, 2)

        return np.maximum(0, out)

    def backward(self, grad):

        import numpy as np

        grad = np.maximum(0, grad)

        N, C, H, W = self._input.shape

        K = self.kernel_size

        S = self.stride

        out_h = grad.shape[2]

        out_w = grad.shape[3]

        grad = grad.transpose(0, 2, 3, 1).reshape(-1, self.out_channels)

        self.grads['W'] = self._col.T @ grad

        self.grads['b'] = np.sum(grad, axis=0)

        dx = grad @ self._col_W.T

        dx = dx.reshape(N, out_h, out_w, C, K, K).transpose(0, 3, 4, 5, 1, 2)

        dx_full = np.zeros((N, C, H + 2*self.padding + S - 1, W + 2*self.padding + S - 1))

        for y in range(K):

            for x_ in range(K):

                dx_full[:, :, y:y+out_h*S:S, x_:x_+out_w*S:S] += dx[:, :, y, x_, :, :]

        if self.padding > 0:

            dx_full = dx_full[:, :, self.padding:-self.padding, self.padding:-self.padding]

        return dx_full

    pass

class Dense:
    """Dense layer."""

    def __init__(self, input_size, output_size, activation='relu'):

        import numpy as np

        self.input_size = input_size

        self.output_size = output_size

        self.activation = activation

        scale = np.sqrt(2.0 / input_size)

        self.params = {'W': np.random.randn(input_size, output_size) * scale, 'b': np.zeros(output_size)}

        self.grads = {'W': np.zeros_like(self.params['W']), 'b': np.zeros_like(self.params['b'])}

    def forward(self, x):

        self._input = x

        out = x @ self.params['W'] + self.params['b']

        if self.activation == 'relu':

            self._mask = out > 0

            out = np.maximum(0, out)

        elif self.activation == 'sigmoid':

            out = 1 / (1 + np.exp(-out))

        elif self.activation == 'tanh':

            out = np.tanh(out)

        elif self.activation == 'linear':

            pass

        elif self.activation == 'softmax':

            exp_out = np.exp(out - np.max(out, axis=-1, keepdims=True))

            out = exp_out / np.sum(exp_out, axis=-1, keepdims=True)

        return out

    def backward(self, grad):

        if self.activation == 'relu':

            grad = grad * self._mask

        elif self.activation == 'sigmoid':

            sig = 1 / (1 + np.exp(-self._input @ self.params['W'] - self.params['b']))

            grad = grad * sig * (1 - sig)

        elif self.activation == 'tanh':

            tanh_out = np.tanh(self._input @ self.params['W'] + self.params['b'])

            grad = grad * (1 - tanh_out**2)

        self.grads['W'] = self._input.T @ grad

        self.grads['b'] = np.sum(grad, axis=0)

        dx = grad @ self.params['W'].T

        return dx

    pass

class Dropout:
    """Dropout layer."""

    def __init__(self, rate=0.5):

        self.rate = rate

        self._mask = None

    def forward(self, x, training=True):

        if training:

            import numpy as np

            self._mask = (np.random.rand(*x.shape) > self.rate).astype(np.float32) / (1 - self.rate)

            return x * self._mask

        return x

    def backward(self, grad):

        if self._mask is not None:

            return grad * self._mask

        return grad

    pass

class LSTM:
    """LSTM layer."""

    def __init__(self, input_size, hidden_size):

        import numpy as np

        self.input_size = input_size

        self.hidden_size = hidden_size

        scale = np.sqrt(2.0 / (input_size + hidden_size))

        self.params = {'W_i': np.random.randn(input_size, 4*hidden_size)*scale, 'W_h': np.random.randn(hidden_size, 4*hidden_size)*scale, 'b': np.zeros(4*hidden_size)}

        self.grads = {'W_i': np.zeros_like(self.params['W_i']), 'W_h': np.zeros_like(self.params['W_h']), 'b': np.zeros_like(self.params['b'])}

        self._input = None

        self._h = None

        self._c = None

        self._c_prev = None

        self._forget_gate = None

        self._input_gate = None

        self._output_gate = None

        self._cell_candidate = None

    def forward(self, x):

        import numpy as np

        self._input = x

        N, T, _ = x.shape

        if self._h is None or self._h.shape[0] != N:

            self._h = np.zeros((N, self.hidden_size))

            self._c = np.zeros((N, self.hidden_size))

        outputs = []

        for t in range(T):

            xt = x[:, t, :]

            self._c_prev = self._c.copy()

            gates = xt @ self.params['W_i'] + self._h @ self.params['W_h'] + self.params['b']

            self._forget_gate = sigmoid(gates[:, :self.hidden_size])

            self._input_gate = sigmoid(gates[:, self.hidden_size:2*self.hidden_size])

            self._cell_candidate = np.tanh(gates[:, 2*self.hidden_size:3*self.hidden_size])

            self._output_gate = sigmoid(gates[:, 3*self.hidden_size:])

            self._c = self._forget_gate * self._c + self._input_gate * self._cell_candidate

            h_t = self._output_gate * np.tanh(self._c)

            self._h = h_t

            outputs.append(h_t)

        return np.stack(outputs, axis=1)

    def backward(self, grad):

        import numpy as np

        N, T, _ = grad.shape

        dW_i = np.zeros_like(self.params['W_i'])

        dW_h = np.zeros_like(self.params['W_h'])

        db = np.zeros_like(self.params['b'])

        dh_next = np.zeros((N, self.hidden_size))

        dc_next = np.zeros((N, self.hidden_size))

        for t in reversed(range(T)):

            dtanh_c = dh_next + dc_next

            doutput_gate = dtanh_c * np.tanh(self._c)

            doutput_gate = sigmoid_derivative(doutput_gate)

            dtanh_c = dtanh_c * self._output_gate * (1 - np.tanh(self._c)**2)

            dcell = dtanh_c + dc_next

            dforget_gate = dcell * self._c_prev if t > 0 else dcell * np.zeros_like(self._c)

            dforget_gate = sigmoid_derivative(dforget_gate)

            dinput_gate = dcell * self._cell_candidate

            dinput_gate = sigmoid_derivative(dinput_gate)

            dcell_candidate = dcell * self._input_gate

            dcell_candidate = dcell_candidate * (1 - self._cell_candidate**2)

            gates = np.concatenate([dforget_gate, dinput_gate, dcell_candidate, doutput_gate], axis=1)

            xt = self._input[:, t, :]

            dh = gates @ self.params['W_h'].T

            dW_i += xt.T @ gates

            dW_h += self._h.T @ gates

            db += np.sum(gates, axis=0)

            dx_t = gates @ self.params['W_i'].T

            dh_next = dh

            dc_next = dcell * self._forget_gate

        self.grads['W_i'] = dW_i

        self.grads['W_h'] = dW_h

        self.grads['b'] = db

        return dx_t.reshape(N, T, -1) if t == 0 else None

    pass

class MaxPool2D:
    """MaxPool2D layer."""

    def __init__(self, pool_size=2, stride=None):

        self.pool_size = pool_size

        self.stride = stride or pool_size

        self._input = None

        self._max_idx = None

    def forward(self, x):

        import numpy as np

        self._input = x

        N, C, H, W = x.shape

        P = self.pool_size

        S = self.stride

        out_h = H // S

        out_w = W // S

        self._max_idx = np.zeros((N, C, out_h, out_w), dtype=np.int32)

        out = np.zeros((N, C, out_h, out_w))

        for n in range(N):

            for c in range(C):

                for i in range(out_h):

                    for j in range(out_w):

                        h_start = i * S

                        w_start = j * S

                        window = x[n, c, h_start:h_start+P, w_start:w_start+P]

                        idx = np.argmax(window)

                        out[n, c, i, j] = window.flat[idx]

                        self._max_idx[n, c, i, j] = idx

        return out

    def backward(self, grad):

        import numpy as np

        N, C, H, W = self._input.shape

        P = self.pool_size

        S = self.stride

        out_h = self._max_idx.shape[2]

        out_w = self._max_idx.shape[3]

        dx = np.zeros_like(self._input)

        for n in range(N):

            for c in range(C):

                for i in range(out_h):

                    for j in range(out_w):

                        h_start = i * S

                        w_start = j * S

                        idx = self._max_idx[n, c, i, j]

                        window = dx[n, c, h_start:h_start+P, w_start:w_start+P]

                        window.flat[idx] = grad[n, c, i, j]

        return dx

    pass


__all__ = ['BatchNorm', 'Conv2D', 'Dense', 'Dropout', 'LSTM', 'MaxPool2D']
