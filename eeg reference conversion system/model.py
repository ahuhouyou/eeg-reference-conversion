import mne

class MY_Model:
    def __init__(self):
        # 标记采用的参考方式
        self.reference = -1

    # 标记使用的参考方式
    def setreference(self, i):
        self.reference = i

    # 转变参考0
    def set_reference(self, channel):
        self.raw_after = self.raw.copy().set_eeg_reference(ref_channels = channel)

    # 转变参考1
    def set_LM(self):
        self.raw_after = self.raw.copy().set_eeg_reference(ref_channels = ['M1', 'M2'])

    # 转变参考2
    def set_AR(self):
        self.raw_after = self.raw.copy().set_eeg_reference(ref_channels="average", projection=True)

    # 转变参考3
    def set_REST(self):
        sphere = mne.make_sphere_model("auto", "auto", self.raw.info)
        src = mne.setup_volume_source_space(sphere=sphere, exclude=30.0, pos=15.0)
        forward = mne.make_forward_solution(self.raw.info, trans=None, src=src, bem=sphere)
        self.raw_after = self.raw.copy().set_eeg_reference("REST", forward=forward)

    # 读取脑电数据
    def dataload(self, path):
        # 标记原始路径
        self.file_path = path
        if path[-3:] == 'set':
            self.raw = mne.io.read_raw_eeglab(path, preload=True)
        elif path[-3:] == 'fif':
            self.raw = mne.io.read_raw_fif(path, preload=True)
        elif path[-3:] == 'edf':
            self.raw = mne.io.read_raw_edf(path, preload=True)

    # 脑电数据裁剪
    def crop(self, t1, t2):
        self.raw.crop(tmin=t1, tmax=t2)

    # 脑电数据滤波
    def filter(self, f1, f2):
        self.raw.filter(l_freq=f1, h_freq=f2)

    # 脑电数据重采样
    def resample(self, f):
        self.raw.resample(sfreq=f)

    # 脑电数据保存
    def save(self, path):
        self.raw_after.save(path, overwrite=True)