import tensorflow as tf

def basic_conv_block(inputs, training, params=None, reuse=None):

    with tf.variable_scope("Basic_conv_block", reuse=reuse):

        if params is None: params = {}
        # Get standard hyperparameters
        bn_momentum = float(params.get('batchnormdecay', 0.99))
        # Get custom hyperparameters
        filters_list = [int(f) for f in
                params.get('basicconvblockfilters').split('|')]
        kernels = [int(k) for k in
                params.get('basicconvblockkernels').split('|')]
        max_pool = bool(params.get('basicconvblockmaxpool', True))
        if max_pool:
            max_pool_size = int(params.get('basicconvblockmaxpoolsize'))
            max_pool_strides = int(params.get('basicconvblockmaxpoolstrides'))
        bottleneck = bool(params.get('basicconvblockbottleneck', False))
        if bottleneck:
            bottleneck_filters = int(
                    params.get('basicconvblockbottleneckfilters'))
        batchnorm = bool(params.get('basicconvblockbatchnorm', False))
        
        x = inputs
        if batchnorm:
            x = tf.layers.batch_normalization(x, momentum=bn_momentum,
                    training=training)

        for i, (filters, kernel_size) in enumerate(zip(filters_list, kernels)):
            x = tf.layers.conv2d(x, filters=filters, kernel_size=kernel_size,
                    activation=tf.nn.relu, padding="same", reuse=reuse,
                    name="conv_{}".format(i+1))
            if max_pool:
                x = tf.layers.max_pooling2d(x, pool_size=max_pool_size,
                        strides=max_pool_strides, name="pool_{}".format(i+1))
            if batchnorm:
                x = tf.layers.batch_normalization(x, momentum=bn_momentum,
                        training=training)

        # bottleneck layer
        if bottleneck:
            x = tf.layers.conv2d(x, filters=bottleneck_filters,
                    kernel_size=1, activation=tf.nn.relu, padding="same",
                    reuse=reuse, name="bottleneck")
            if batchnorm:
                x = tf.layers.batch_normalization(x, momentum=bn_momentum,
                        training=training)

    return x

def basic_fc_head(inputs, training, params=None):

    # Get standard hyperparameters
    if params is None: params = {}
    num_classes = params.get('num_classes', 2)
    bn_momentum = float(params.get('batchnormdecay', 0.99))
    
    # Get custom hyperparameters
    layers = [int(l) for l in params.get('basicfcheadlayers').split('|')]
    batchnorm = bool(params.get('basicfcheadbatchnorm', False))

    x = tf.layers.flatten(inputs)

    for i, units in enumerate(layers):
        x = tf.layers.dense(x, units=units, activation=tf.nn.relu,
                name="fc_{}".format(i+1))
        if batchnorm:
            x = tf.layers.batch_normalization(x, momentum=bn_momentum,
                    training=training)

    logits = tf.layers.dense(x, units=num_classes, name="logits")

    return logits

def basic_conv_head(inputs, training, params=None):

    # Get standard hyperparameters
    if params is None: params = {}
    num_classes = params.get('num_classes', 2)
    bn_momentum = float(params.get('batchnormdecay', 0.99))
    
    # Get custom hyperparameters
    filters_list = [int(f) for f in
            params.get('basicconvheadfilters').split('|')]
    kernels = [int(k) for k in
            params.get('basicconvheadkernels').split('|')]
    avg_pool = bool(params.get('basicconvheadavgpool', True))
    batchnorm = bool(params.get('basicconvheadbatchnorm', False))

    x = inputs

    for i, (filters, kernel_size) in enumerate(zip(filters_list, kernels)):
        x = tf.layers.conv2d(x, filters=filters, kernel_size=kernel_size,
                activation=tf.nn.relu, padding="same",
                name="conv_{}".format(i+1))
        if batchnorm:
            x = tf.layers.batch_normalization(x, momentum=bn_momentum,
                    training=training)

    # Average over remaining width and length
    if avg_pool:
        x = tf.layers.average_pooling2d(x,
                pool_size=x.get_shape().as_list()[1],
                strides=1, name="global_avg_pool")
    
    flatten = tf.layers.flatten(x)
    logits = tf.layers.dense(flatten, units=num_classes, name="logits")

    return logits


