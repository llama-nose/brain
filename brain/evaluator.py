import numpy as np
from scipy.spatial.distance import mahalanobis
from scipy.linalg import inv
from sklearn.covariance import LedoitWolf
from sklearn.manifold import TSNE
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler


class Evaluator():
    def __init__(self, embeddings, verbose=True):
        
        self.verbose = verbose
        self.embeddings = self._preprocess_embeddings(embeddings)
        self.num_samples, self.embedding_dim = self.embeddings.shape

        return
        

    def _preprocess_embeddings(self, embeddings):
        # Standardize the data
        self.scaler = StandardScaler()
        embeddings_scaled = self.scaler.fit_transform(embeddings)

        # Apply PCA
        self.pca = PCA(n_components=0.95)
        embeddings_reduced = self.pca.fit_transform(embeddings_scaled)

        if self.verbose:
            # Check how many components were kept
            print(f"Reduced dimensionality from 1536 to {embeddings_reduced.shape[1]} dimensions.")

            # Optional: Check explained variance
            print(f"Explained variance ratio: {self.pca.explained_variance_ratio_}")

        return embeddings_reduced


    def _fit_multivariate_gaussian(self, embeddings):

        self.mean = np.mean(embeddings, axis=0)
        self.covariance = LedoitWolf().fit(embeddings).covariance_ + 1e-6*np.eye(embeddings.shape[1])
        # self.covariance = np.cov(embeddings, rowvar=False) # Use this if there are more samples than features

        return
    

    def _mahalanobis_distance(self, sample:np.ndarray) -> float:
        # Check if the sample is the right shape
        if sample.shape != self.mean.shape:
            raise ValueError(f"Sample shape {sample.shape} does not match mean shape {self.mean.shape}")

        return mahalanobis(sample, self.mean, inv(self.covariance))
    

    def fit(self) -> None:
        # Fit the gaussian
        self._fit_multivariate_gaussian(self.embeddings)

        return
    

    def _project_tsne(self, embeddings):
        tsne = TSNE(n_components=2, 
                    perplexity=self.num_samples//3, 
                    random_state=42, 
                    metric='mahalanobis',
                    init='random', 
                    learning_rate=200)
        vis_dims = tsne.fit_transform(embeddings)
        return vis_dims

    def evaluate(self, sample) -> float:
        
        # Preprocess the new sample
        sample = self.pca.transform(self.scaler.transform(sample.reshape(1, -1))).flatten()

        distance = self._mahalanobis_distance(sample)

        return distance
    

if __name__ == '__main__':

    lln_evaluator = Evaluator('../data/animals.npy')
    lln_evaluator.fit()

    sample = np.load('../data/bed.npy').flatten()
    distance = lln_evaluator.evaluate(sample)
    print(f"bed distance: {distance:0.2f}")

    sample = np.load('../data/cheetah.npy').flatten()
    distance = lln_evaluator.evaluate(sample)
    print(f"cheetah distance: {distance:0.2f}")

    sample = np.load('../data/cat.npy').flatten()
    distance = lln_evaluator.evaluate(sample)
    print(f"cat distance: {distance:0.2f}")

    pass