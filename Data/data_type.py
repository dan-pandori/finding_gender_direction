import random
from pandas import DataFrame

class DataStorage:
    def __init__(self, data, batch_size = 1024, rand_seed = 42, train_test_ratio = 0.9) -> None:

        '''
        A class to easily use the data to learn conceptual directions (hyperplanes). It takes a DataFrame with columns:
        - 'sentences' : the list of all sentencesthat are going to be used for training. 
            The last token is the only on on which the hyperplane is learnt.
        - 'label' : names for classes that are meaningfully differents, for example 'pronouns', 'nouns', 'names'. You can
            you can learn them separatly.
        - 'bin' : a binary variable, to identify a concept and its opposite, for example 'male' and 'female'. They should
             be represented by +1 or -1.
        '''
        
        self.data : DataFrame = data
        self.nb_class : int = data['label'].nunique()
        self.label_names : list[str] = data['label'].unique()
        self.is_training : list[bool]
        self.dim_labels : list[list[int]]

        self.batch_size : int = batch_size
        self.rand_seed : int = rand_seed
        self.train_test_ratio : int = train_test_ratio

        self.init_train_test()
        self.init_labels()


    def init_labels(self) -> None:
        '''
        Transform the labels into a nb_class vector with one binary coordinate.
        '''
        dim_labels = []
        for label, valence in zip(self.data['label'], self.data['bin']):
            dim_label = [0]*self.nb_class
            for i, name in enumerate(self.label_names):
                if label == name:
                    dim_label[i] = valence
            dim_labels.append(dim_label)

        self.dim_labels = dim_labels


    def init_train_test(self) -> None:
        '''
        Initialise which data will be in training and which will be in test.
        We garantee the same proportion of train and test for each class.
        '''
        random.seed(self.rand_seed)
        self.is_training = [True]*len(self.data['examples'])

        for name in self.label_names:
            training = []
            nb_data = len(self.data[self.data['label'] == name])
            nb_train = int(self.train_test_ratio*nb_data)
            training = [True]*nb_train + [False]*(nb_data - nb_train)
            random.shuffle(training)

            index = 0
            for i, ex_name in enumerate(self.data['label']):
                if ex_name == name:
                    self.is_training[i] = training[index]
                    index += 1


    def batch(self, list : list[str]) -> list[list[str]]:
        '''
        Transform the data into subsets of size at most bach_size.
        '''
        Nb_ex = len(list)
        Nb_batch = Nb_ex//self.batch_size + 1
        return [list[i*self.batch_size:min((i+1)*self.batch_size, Nb_ex)] for i in range(Nb_batch)]


    def get_ex(self, method, multi_dim=True, label='all') -> list[list[str, list[int]]]:
        '''
        Returns the batched data to train, test, or learn the hyperplanes.
        Train and Test splits the data into different subsets, and respect the class proportions.
        In each case, you can choose to only take a single classes of examples.
        '''
        labels = self.get_labels(multi_dim=multi_dim)
        sentences = self.data['examples']
        if label == 'all':
            is_names = [True]*len(sentences)
        else:
            is_names = (self.data['label'] == label).values.tolist()
        if method == 'train':
            examples = [[sentence, label] for sentence, label, is_train, is_name in zip(sentences, labels, self.is_training, is_names) if is_train and is_name]
        elif method == 'test':
            examples = [[sentence, label] for sentence, label, is_train, is_name in zip(sentences, labels, self.is_training, is_names) if (not is_train) and is_name]
        elif method == 'learn':
            examples = [[sentence, label] for sentence, label, is_name in zip(sentences, labels, is_names) if is_name]
        return self.batch(examples)


    def get_labels(self, multi_dim=True) -> list[list[int]]:
        '''
        Changes the format of the labels if you want to have it one dimensional or not, and returns them.
        '''
        if multi_dim:
            return self.dim_labels
        else:
            return [[1] if (1 in label) else [-1] for label in self.dim_labels]