from tensorflow.python.keras import backend as K
from tensorflow.python.keras.models import Model
from tensorflow.python.keras.layers import Flatten, Dense, Dropout
from tensorflow.python.keras.applications.resnet50 import ResNet50
from tensorflow.python.keras.optimizers import Adam
from tensorflow.python.keras.preprocessing.image import ImageDataGenerator

# ��Ƹ��|
DATASET_PATH  = 'sample'

# �v���j�p
IMAGE_SIZE = (224, 224)

# �v�����O��
NUM_CLASSES = 2

# �Y GPU �O���餣���A�i�խ� batch size �έᵲ��h�h����
BATCH_SIZE = 8

# �ᵲ�����h��
FREEZE_LAYERS = 2

# Epoch ��
NUM_EPOCHS = 20

# �ҫ���X�x�s���ɮ�
WEIGHTS_FINAL = 'model-resnet50-final.h5'

# �z�L data augmentation ���ͰV�m�P���ҥΪ��v�����
train_datagen = ImageDataGenerator(rotation_range=40,
                                   width_shift_range=0.2,
                                   height_shift_range=0.2,
                                   shear_range=0.2,
                                   zoom_range=0.2,
                                   channel_shift_range=10,
                                   horizontal_flip=True,
                                   fill_mode='nearest')
train_batches = train_datagen.flow_from_directory(DATASET_PATH + '/train',
                                                  target_size=IMAGE_SIZE,
                                                  interpolation='bicubic',
                                                  class_mode='categorical',
                                                  shuffle=True,
                                                  batch_size=BATCH_SIZE)

valid_datagen = ImageDataGenerator()
valid_batches = valid_datagen.flow_from_directory(DATASET_PATH + '/valid',
                                                  target_size=IMAGE_SIZE,
                                                  interpolation='bicubic',
                                                  class_mode='categorical',
                                                  shuffle=False,
                                                  batch_size=BATCH_SIZE)

# ��X�U���O�����ޭ�
for cls, idx in train_batches.class_indices.items():
    print('Class #{} = {}'.format(idx, cls))

# �H�V�m�n�� ResNet50 ����¦�ӫإ߼ҫ��A
# �˱� ResNet50 ���h�� fully connected layers
net = ResNet50(include_top=False, weights='imagenet', input_tensor=None,
               input_shape=(IMAGE_SIZE[0],IMAGE_SIZE[1],3))
x = net.output
x = Flatten()(x)

# �W�[ DropOut layer
x = Dropout(0.5)(x)

# �W�[ Dense layer�A�H softmax ���ͭ����O�����v��
output_layer = Dense(NUM_CLASSES, activation='softmax', name='softmax')(x)

# �]�w�ᵲ�P�n�i��V�m�������h
net_final = Model(inputs=net.input, outputs=output_layer)
for layer in net_final.layers[:FREEZE_LAYERS]:
    layer.trainable = False
for layer in net_final.layers[FREEZE_LAYERS:]:
    layer.trainable = True

# �ϥ� Adam optimizer�A�H���C�� learning rate �i�� fine-tuning
net_final.compile(optimizer=Adam(lr=1e-5),
                  loss='categorical_crossentropy', metrics=['accuracy'])

# ��X��Ӻ������c
print(net_final.summary())

# �V�m�ҫ�
net_final.fit_generator(train_batches,
                        steps_per_epoch = train_batches.samples // BATCH_SIZE,
                        validation_data = valid_batches,
                        validation_steps = valid_batches.samples // BATCH_SIZE,
                        epochs = NUM_EPOCHS)

# �x�s�V�m�n���ҫ�
net_final.save(WEIGHTS_FINAL)