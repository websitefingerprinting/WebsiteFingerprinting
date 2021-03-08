import torch
import torch.nn as nn
import numpy as np
import time
import random
import argparse
import configparser
import logging
import const
from sklearn.model_selection import StratifiedShuffleSplit
from torchsummary import summary
import torch.utils.data as Data
from torchmodel import DF

# Device configuration
device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')

# Hyper parameters
num_epochs = 20
batch_size = 128
length = 10000
mask_length = length


def read_conf(file):
    cf = configparser.ConfigParser()
    cf.read(file)
    return dict(cf['default'])


def init_logger():
    logger = logging.getLogger('df')
    logger.setLevel(logging.DEBUG)
    # create console handler and set level to debug
    ch = logging.StreamHandler()
    # create formatter
    formatter = logging.Formatter(const.LOG_FORMAT)
    # add formatter to ch
    ch.setFormatter(formatter)
    # add ch to logger
    logger.addHandler(ch)
    return logger


def load_data(fpath):
    train = np.load(fpath, allow_pickle=True).item()
    X, y = train['feature'], train['label']
    return X, y


def score_func(predictions, ground_truths, mon_site_num):
    tp, wp, fp, p, n = 0, 0, 0, 0 ,0
    for truth,prediction in zip(ground_truths, predictions):
        if truth != mon_site_num:
            p += 1
        else:
            n += 1
        if prediction != mon_site_num:
            if truth == prediction:
                tp += 1
            else:
                if truth != mon_site_num:
                    wp += 1
                else:
                    fp += 1
    return tp, wp, fp, p, n



if __name__ == '__main__':
    cf = read_conf(const.confdir)
    MON_SITE_NUM = int(cf['monitored_site_num'])
    open_world = int(cf['open_world'])
    random.seed(0)
    '''initialize logger'''
    logger = init_logger()
    '''read config'''
    parser = argparse.ArgumentParser(description='DF attack')
    parser.add_argument('feature_path',
                        metavar='<feature path>',
                        help='Path to the directory of the extracted features')
    args = parser.parse_args()

    X, y = load_data(args.feature_path)
    X = X[:, :length]
    X = X.astype('float32')

    # we need a [Length x 1] x n shape as input to the DFNet (Tensorflow)
    if len(X.shape) < 3:
        X = X[:, :, np.newaxis]
    if len(y.shape) > 1 and y.shape[1] > 1:
        y = np.argmax(y, axis=1)

    if not open_world:
        X = X[y < MON_SITE_NUM]
        y = y[y < MON_SITE_NUM]
    num_classes = MON_SITE_NUM + open_world
    # X = X[:,:cut_length,:]
    X = torch.from_numpy(X).permute(0, 2, 1)
    y = torch.from_numpy(y)


    sss = StratifiedShuffleSplit(n_splits=10, test_size=0.1, random_state=0)
    tps, wps, fps, ps, ns = 0, 0, 0, 0, 0
    start_time = time.time()
    folder_num = 0
    for train_index, test_index in sss.split(X, y):
        folder_num += 1
        # if folder_num > 2:
        #     break

        model = DF(length, num_classes).to(device)
        # summary(model, (1, length))
        # Loss and optimizer
        criterion = nn.CrossEntropyLoss()
        optimizer = torch.optim.Adamax(model.parameters())

        X_train, X_test = X[train_index], X[test_index]
        y_train, y_test = y[train_index], y[test_index]

        # logger.info("train shape: {} {}".format(X_train.data.shape, y_train.data.shape))
        # logger.info("test shape: {} {}".format(X_test.data.shape, y_test.data.shape))
        # remove synthesized traces in testset, meanwhile, fix labels for trainset
        X_test = X_test[y_test >= 0]
        y_test = y_test[y_test >= 0]
        y_train[y_train < 0] = -(y_train[y_train < 0] + 1)
        assert np.all(y_train.numpy() >= 0) and np.all(y_test.numpy() >= 0)
        logger.info("train shape: {} {}".format(X_train.data.shape, y_train.data.shape))
        logger.info("test shape: {} {}".format(X_test.data.shape, y_test.data.shape))
        # (unique, counts) = np.unique(y_train, return_counts=True)
        # frequencies = np.asarray((unique, counts)).T
        # print(frequencies)

        train_dataset = Data.TensorDataset(X_train, y_train)
        test_dataset = Data.TensorDataset(X_test, y_test)

        train_loader = Data.DataLoader(
            dataset=train_dataset,  # torch TensorDataset format
            batch_size=batch_size,  # mini batch size
            shuffle=True,
            num_workers=2,
        )
        test_loader = Data.DataLoader(
            dataset=test_dataset,  # torch TensorDataset format
            batch_size=batch_size,  # mini batch size
            shuffle=False,
            num_workers=2,
        )
        total_step = len(train_loader)
        for epoch in range(num_epochs):
            for step, (batch_x, batch_y) in enumerate(train_loader):
                batch_x = batch_x.to(device)
                batch_y = batch_y.to(device)
                # Forward pass
                outputs = model(batch_x)
                loss = criterion(outputs, batch_y)

                # Backward and optimize
                optimizer.zero_grad()
                loss.backward()
                optimizer.step()

                if (step + 1) % 50 == 0:
                    logger.info('Epoch [{}/{}], Step [{}/{}], Loss: {:.4f}'
                          .format(epoch + 1, num_epochs, step + 1, total_step, loss.item()))
        # Test the model
        model.eval()  # eval mode (batchnorm uses moving mean/variance instead of mini-batch mean/variance)
        with torch.no_grad():
            correct = 0
            total = 0
            for batch_x, batch_y in test_loader:
                batch_x = batch_x.to(device)
                batch_y = batch_y.to(device)
                outputs = model(batch_x)
                _, predicted = torch.max(outputs.data, 1)
                # print(predicted)
                tp, wp, fp, p, n = score_func(predicted.data.cpu().numpy(), batch_y.data.cpu().numpy(), MON_SITE_NUM)
                logger.info("Fold #{}: {} {} {} {} {}".format(folder_num, tp, wp, fp, p, n))
                tps, wps, fps, ps, ns = tps + tp, wps + wp, fps + fp, ps + p, ns + n
                # total += batch_y.size(0)
                # correct += (predicted == batch_y).sum().item()
        del model
            # print('Test Accuracy on {} examples: {} %'.format(total, 100 * correct / total))
        # Save the model checkpoint
        # torch.save(model.state_dict(), 'models/df.ckpt')
    logger.info("{} {} {} {} {}\n".format(tps, wps, fps, ps, ns))
