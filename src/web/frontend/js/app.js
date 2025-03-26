// 导入组件
const { createApp, ref, reactive, onMounted, computed, watch } = Vue;
const { ElMessage, ElLoading } = ElementPlus;

// 定义API基础URL
const API_BASE_URL = 'http://localhost:8000';
const WS_BASE_URL = 'ws://localhost:8000';

// 创建Vue应用
const app = createApp({
    setup() {
        // 表单数据
        const formData = reactive({
            save_folder: 'data/dataset',
            video_file_path: '',
            is_debrisflow: true,
            data_type: 'train',
            frame_idx: 1000,
            slice_windows_size: 75,
            extract_freq: 1,
            point_coordinates: [[800, 700]],
            sam_video_sign: true,
            sam_model_type: 'vit_h',
            sam_model_device: 'auto', // auto为自动选择，将在后端处理
            sam_checkpoint: 'models/pretrained/sam/sam_vit_h_4b8939.pth',
            // 批处理模式
            batch_mode: false,
            batch_start_frame: 0,
            batch_end_frame: 2000,
            batch_step: 20 // 每隔多少帧处理一次
        });

        // 视频列表
        const videoList = ref([]);
        
        // 当前选中的视频信息
        const selectedVideoInfo = ref(null);
        
        // WebSocket连接
        const ws = ref(null);
        
        // 处理进度
        const processProgress = reactive({
            visible: false,
            percent: 0,
            message: ''
        });
        
        // 帧图像数据
        const frameImages = ref({
            start_frame: null,
            end_frame: null,
            start_idx: 0,
            end_idx: 0
        });
        
        // 图像加载状态
        const isLoadingFrames = ref(false);
        
        // 表单引用
        const formRef = ref(null);
        
        // 上传文件的引用
        const uploadRef = ref(null);
        
        // 是否正在处理
        const isProcessing = ref(false);
        
        // 处理结果
        const processResult = ref(null);

        // 计算属性：视频是否已选择
        const isVideoSelected = computed(() => {
            return formData.video_file_path !== '';
        });
        
        // 监听视频选择
        watch(() => formData.video_file_path, (newVal) => {
            if (newVal) {
                // 查找选择的视频信息
                const video = videoList.value.find(v => v.path === newVal);
                if (video) {
                    selectedVideoInfo.value = video.info;
                    
                    // 如果帧索引超过了视频总帧数，重置为视频总帧数的80%位置
                    if (formData.frame_idx >= video.info.total_frames) {
                        formData.frame_idx = Math.floor(video.info.total_frames * 0.8);
                    }
                    
                    // 加载帧图像
                    loadFrameImages();
                }
            } else {
                selectedVideoInfo.value = null;
                frameImages.value = {
                    start_frame: null,
                    end_frame: null,
                    start_idx: 0,
                    end_idx: 0
                };
            }
        });
        
        // 监听帧索引、窗口大小和提取频率的变化
        watch([() => formData.frame_idx, () => formData.slice_windows_size, () => formData.extract_freq], 
            () => {
                if (formData.video_file_path) {
                    loadFrameImages();
                }
            }
        );

        // 监听批处理参数的变化，更新预览帧
        watch(
            [
                () => formData.batch_mode, 
                () => formData.batch_start_frame, 
                () => formData.batch_end_frame
            ], 
            () => {
                if (formData.video_file_path && selectedVideoInfo.value) {
                    // 确保批处理参数在有效范围内
                    if (formData.batch_mode) {
                        // 确保结束帧不超过视频总帧数
                        if (formData.batch_end_frame >= selectedVideoInfo.value.total_frames) {
                            formData.batch_end_frame = selectedVideoInfo.value.total_frames - 1;
                        }
                        
                        // 确保起始帧小于等于结束帧
                        if (formData.batch_start_frame > formData.batch_end_frame) {
                            formData.batch_start_frame = formData.batch_end_frame;
                        }
                        
                        // 使用批处理的起始帧作为预览帧
                        formData.frame_idx = formData.batch_start_frame;
                    }
                    loadFrameImages();
                }
            }
        );

        // 监听兴趣点坐标的变化
        watch(() => formData.point_coordinates, () => {
            if (formData.video_file_path) {
                loadFrameImages();
            }
        }, { deep: true });

        // 获取视频列表
        const fetchVideoList = async () => {
            try {
                const response = await axios.get(`${API_BASE_URL}/list_videos`);
                videoList.value = response.data.videos;
            } catch (error) {
                console.error('获取视频列表失败:', error);
                ElMessage.error('获取视频列表失败');
            }
        };
        
        // 加载帧图像
        const loadFrameImages = async () => {
            if (!formData.video_file_path) return;
            
            isLoadingFrames.value = true;
            try {
                // 在批处理模式下，加载起始帧和结束帧的预览
                if (formData.batch_mode) {
                    try {
                        // 加载起始帧
                        const startResponse = await axios.get(`${API_BASE_URL}/frame_images`, {
                            params: {
                                video_path: formData.video_file_path,
                                frame_idx: formData.batch_start_frame,
                                window_size: formData.slice_windows_size,
                                extract_freq: formData.extract_freq,
                                point_coordinates: JSON.stringify(formData.point_coordinates)
                            }
                        });
                        
                        // 加载结束帧
                        const endResponse = await axios.get(`${API_BASE_URL}/frame_images`, {
                            params: {
                                video_path: formData.video_file_path,
                                frame_idx: formData.batch_end_frame,
                                window_size: formData.slice_windows_size,
                                extract_freq: formData.extract_freq,
                                point_coordinates: JSON.stringify(formData.point_coordinates)
                            }
                        });
                        
                        // 合并结果
                        frameImages.value = {
                            start_frame: startResponse.data.start_frame,
                            end_frame: endResponse.data.start_frame,  // 使用结束帧的第一帧作为结束帧显示
                            start_idx: formData.batch_start_frame,
                            end_idx: formData.batch_end_frame
                        };
                    } catch (err) {
                        console.error('获取批处理预览帧失败:', err);
                        ElMessage.error('获取批处理预览帧失败，请检查帧索引是否有效');
                        
                        // 如果获取批处理预览失败，退回到单帧模式的预览
                        const response = await axios.get(`${API_BASE_URL}/frame_images`, {
                            params: {
                                video_path: formData.video_file_path,
                                frame_idx: formData.frame_idx,
                                window_size: formData.slice_windows_size,
                                extract_freq: formData.extract_freq,
                                point_coordinates: JSON.stringify(formData.point_coordinates)
                            }
                        });
                        
                        frameImages.value = response.data;
                    }
                } else {
                    // 单帧模式，使用原来的逻辑
                    const response = await axios.get(`${API_BASE_URL}/frame_images`, {
                        params: {
                            video_path: formData.video_file_path,
                            frame_idx: formData.frame_idx,
                            window_size: formData.slice_windows_size,
                            extract_freq: formData.extract_freq,
                            point_coordinates: JSON.stringify(formData.point_coordinates)
                        }
                    });
                    
                    frameImages.value = response.data;
                }
            } catch (error) {
                console.error('获取帧图像失败:', error);
                ElMessage.error('获取帧图像失败，请检查视频文件和参数');
            } finally {
                isLoadingFrames.value = false;
            }
        };
        
        // 在图像上选择兴趣点
        const selectPointOnImage = (event, imageElement) => {
            if (!imageElement) return;
            
            // 获取图像元素的尺寸和位置
            const rect = imageElement.getBoundingClientRect();
            
            // 计算相对于图像的点击位置
            const x = event.clientX - rect.left;
            const y = event.clientY - rect.top;
            
            // 计算相对坐标（0-1范围内）
            const relX = x / rect.width;
            const relY = y / rect.height;
            
            // 如果有选中的视频信息，计算实际的兴趣点坐标
            if (selectedVideoInfo.value) {
                // 获取分辨率
                const resolution = selectedVideoInfo.value.resolution.split('x');
                if (resolution.length === 2) {
                    const width = parseInt(resolution[0]);
                    const height = parseInt(resolution[1]);
                    
                    // 计算实际坐标
                    const newPoint = [
                        Math.round(relX * width),
                        Math.round(relY * height)
                    ];
                    
                    // 添加新的点到列表中
                    formData.point_coordinates.push(newPoint);
                    
                    ElMessage.success(`已添加兴趣点坐标: [${newPoint[0]}, ${newPoint[1]}]`);
                    
                    // 重新加载帧图像以显示兴趣点
                    loadFrameImages();
                }
            }
        };

        // 删除选中的兴趣点
        const removePoint = (index) => {
            formData.point_coordinates.splice(index, 1);
            ElMessage.success('已删除选中的兴趣点');
            loadFrameImages();
        };

        // 清空所有兴趣点
        const clearPoints = () => {
            formData.point_coordinates = [];
            ElMessage.success('已清空所有兴趣点');
            loadFrameImages();
        };

        // 解析输入的坐标文本
        const parseCoordinatesText = (text) => {
            try {
                // 移除所有空格
                text = text.replace(/\s+/g, '');
                // 检查基本格式
                if (!text.startsWith('[[') || !text.endsWith(']]')) {
                    throw new Error('格式错误：请使用[[x1,y1],[x2,y2],...]格式');
                }
                // 提取内部内容
                text = text.slice(2, -2);
                // 分割每个点
                const points = text.split('],[').map(point => {
                    const [x, y] = point.split(',').map(num => parseInt(num.trim()));
                    if (isNaN(x) || isNaN(y)) {
                        throw new Error('坐标必须是数字');
                    }
                    return [x, y];
                });
                return points;
            } catch (error) {
                throw new Error(`解析失败：${error.message}`);
            }
        };

        // 添加一个新的响应式变量用于存储输入的文本
        const coordinatesText = ref('');

        // 修改处理坐标文本输入的函数
        const handleCoordinatesInput = (text) => {
            try {
                const points = parseCoordinatesText(text);
                formData.point_coordinates = points;
                ElMessage.success(`成功添加 ${points.length} 个坐标点`);
                loadFrameImages();
            } catch (error) {
                ElMessage.error(error.message);
            }
        };

        // 监听文本输入的变化
        watch(coordinatesText, (newValue) => {
            if (newValue.trim()) {
                handleCoordinatesInput(newValue);
            }
        });

        // 选择视频
        const selectVideo = (videoPath) => {
            formData.video_file_path = videoPath;
        };
        
        // 上传视频
        const uploadVideo = async (file) => {
            const loading = ElLoading.service({
                lock: true,
                text: '上传中...',
                background: 'rgba(0, 0, 0, 0.7)'
            });
            
            try {
                const formData = new FormData();
                formData.append('file', file);
                
                const response = await axios.post(`${API_BASE_URL}/upload_video`, formData, {
                    headers: {
                        'Content-Type': 'multipart/form-data'
                    }
                });
                
                ElMessage.success('视频上传成功');
                await fetchVideoList(); // 更新视频列表
                
                return {
                    file_path: response.data.file_path,
                    video_info: response.data.video_info
                };
            } catch (error) {
                console.error('视频上传失败:', error);
                ElMessage.error('视频上传失败');
                return null;
            } finally {
                loading.close();
            }
        };
        
        // 文件上传之前的钩子
        const beforeUpload = (file) => {
            const isVideo = file.type.indexOf('video') !== -1;
            if (!isVideo) {
                ElMessage.error('只能上传视频文件!');
                return false;
            }
            
            const isLt500M = file.size / 1024 / 1024 < 500;
            if (!isLt500M) {
                ElMessage.error('视频大小不能超过 500MB!');
                return false;
            }
            
            return true;
        };
        
        // 文件上传成功的钩子
        const onUploadSuccess = async (response, file, fileList) => {
            formData.video_file_path = response.file_path;
            selectedVideoInfo.value = response.video_info;
            ElMessage.success(`${file.name} 上传成功`);
            
            // 加载帧图像
            loadFrameImages();
        };
        
        // 提交表单
        const submitForm = async () => {
            if (!formRef.value) return;
            
            await formRef.value.validate(async (valid) => {
                if (valid) {
                    // 验证通过，提交表单
                    const loading = ElLoading.service({
                        lock: true,
                        text: formData.batch_mode ? '批量处理中...' : '处理中...',
                        background: 'rgba(0, 0, 0, 0.7)'
                    });
                    
                    isProcessing.value = true;
                    processResult.value = null;
                    
                    try {
                        // 准备请求数据，将 'auto' 设备转换为 null
                        const requestData = {...formData};
                        if (requestData.sam_model_device === 'auto') {
                            requestData.sam_model_device = null;
                        }
                        
                        const response = await axios.post(`${API_BASE_URL}/make_dataset`, requestData);
                        
                        processResult.value = response.data;
                        
                        // 区分批处理和单帧处理的成功提示
                        if (formData.batch_mode) {
                            const successCount = response.data.results.filter(r => r.success).length;
                            const totalCount = response.data.results.length;
                            ElMessage.success(`批处理完成，共处理 ${totalCount} 个视频片段，成功 ${successCount} 个`);
                        } else {
                            ElMessage.success('数据集创建成功');
                        }
                    } catch (error) {
                        console.error('处理失败:', error);
                        ElMessage.error(`处理失败: ${error.response?.data?.detail || error.message}`);
                    } finally {
                        loading.close();
                        isProcessing.value = false;
                    }
                } else {
                    ElMessage.error('请填写所有必填项');
                    return false;
                }
            });
        };
        
        // 重置表单
        const resetForm = () => {
            if (formRef.value) {
                formRef.value.resetFields();
                processResult.value = null;
                selectedVideoInfo.value = null;
                frameImages.value = {
                    start_frame: null,
                    end_frame: null,
                    start_idx: 0,
                    end_idx: 0
                };
            }
        };
        
        // 自定义上传方法
        const customUpload = async (params) => {
            const { file } = params;
            const result = await uploadVideo(file);
            if (result) {
                params.onSuccess({
                    file_path: result.file_path,
                    video_info: result.video_info
                });
            } else {
                params.onError(new Error('上传失败'));
            }
        };
        
        // 格式化文件大小
        const formatFileSize = (size) => {
            if (size < 1024) {
                return size + ' B';
            } else if (size < 1024 * 1024) {
                return (size / 1024).toFixed(2) + ' KB';
            } else if (size < 1024 * 1024 * 1024) {
                return (size / 1024 / 1024).toFixed(2) + ' MB';
            } else {
                return (size / 1024 / 1024 / 1024).toFixed(2) + ' GB';
            }
        };
        
        // 生命周期钩子
        onMounted(() => {
            // 组件挂载后，获取视频列表
            fetchVideoList();
            
            // 连接WebSocket
            connectWebSocket();
        });
        
        // 连接WebSocket
        const connectWebSocket = () => {
            // 创建WebSocket连接
            ws.value = new WebSocket(`${WS_BASE_URL}/ws`);
            
            // 处理连接打开
            ws.value.onopen = () => {
                console.log('WebSocket连接已建立');
            };
            
            // 处理接收到的消息
            ws.value.onmessage = (event) => {
                const data = JSON.parse(event.data);
                if (data.progress !== undefined) {
                    processProgress.percent = data.progress;
                    processProgress.message = data.message;
                    processProgress.visible = true;
                    
                    // 如果进度达到100%，延迟关闭进度条
                    if (data.progress === 100) {
                        setTimeout(() => {
                            processProgress.visible = false;
                        }, 2000);
                    }
                }
            };
            
            // 处理连接关闭
            ws.value.onclose = () => {
                console.log('WebSocket连接已关闭');
                // 尝试重新连接
                setTimeout(connectWebSocket, 2000);
            };
            
            // 处理错误
            ws.value.onerror = (error) => {
                console.error('WebSocket错误:', error);
            };
        };
        
        // 添加单点输入的数据
        const newPoint = reactive({
            x: 0,
            y: 0
        });

        // 添加单点的方法
        const addSinglePoint = () => {
            formData.point_coordinates.push([newPoint.x, newPoint.y]);
            ElMessage.success(`已添加兴趣点坐标: [${newPoint.x}, ${newPoint.y}]`);
            newPoint.x = 0;
            newPoint.y = 0;
            loadFrameImages();
        };

        // 返回需要暴露给模板的属性和方法
        return {
            formData,
            videoList,
            selectedVideoInfo,
            processProgress,
            frameImages,
            isLoadingFrames,
            formRef,
            uploadRef,
            isProcessing,
            processResult,
            isVideoSelected,
            coordinatesText,
            newPoint,
            fetchVideoList,
            selectVideo,
            uploadVideo,
            beforeUpload,
            onUploadSuccess,
            submitForm,
            resetForm,
            customUpload,
            formatFileSize,
            loadFrameImages,
            selectPointOnImage,
            removePoint,
            clearPoints,
            handleCoordinatesInput,
            addSinglePoint
        };
    },
    template: `
    <div class="app-container">
        <header class="app-header">
            <h1 class="app-title">泥石流视频处理系统</h1>
        </header>
        
        <div class="app-content">
            <el-card class="video-processor">
                <template #header>
                    <div class="card-header">
                        <h2>视频处理参数设置</h2>
                    </div>
                </template>
                
                <!-- 进度条 -->
                <el-dialog
                    v-model="processProgress.visible"
                    title="批量处理进度"
                    :show-close="false"
                    :close-on-click-modal="false"
                    :close-on-press-escape="false"
                    width="500px"
                >
                    <div class="progress-container">
                        <p class="progress-message">{{ processProgress.message }}</p>
                        <el-progress 
                            :percentage="processProgress.percent" 
                            :format="(percent) => Math.floor(percent) + '%'" 
                            :stroke-width="20" 
                            status="success"
                        ></el-progress>
                    </div>
                </el-dialog>
                
                <el-form ref="formRef" :model="formData" label-width="140px" label-position="left" :rules="formRules">
                    <div class="form-section">
                        <h2 class="form-section-title">视频选择</h2>
                        
                        <div class="upload-wrapper">
                            <el-upload
                                ref="uploadRef"
                                action=""
                                :http-request="customUpload"
                                :before-upload="beforeUpload"
                                :on-success="onUploadSuccess"
                                :limit="1"
                                :auto-upload="true"
                                accept="video/*"
                            >
                                <el-button type="primary">上传视频</el-button>
                                <template #tip>
                                    <div class="el-upload__tip">
                                        请上传视频文件（MP4、AVI等格式，大小不超过500MB）
                                    </div>
                                </template>
                            </el-upload>
                        </div>
                        
                        <el-form-item label="选择已有视频" prop="video_file_path">
                            <el-select 
                                v-model="formData.video_file_path" 
                                placeholder="请选择视频文件" 
                                style="width: 100%"
                                filterable
                            >
                                <el-option
                                    v-for="video in videoList"
                                    :key="video.path"
                                    :label="video.name"
                                    :value="video.path"
                                >
                                    <div style="display: flex; justify-content: space-between; align-items: center">
                                        <span>{{ video.name }}</span>
                                        <span style="color: #8492a6; font-size: 13px">
                                            {{ formatFileSize(video.size) }}
                                        </span>
                                    </div>
                                </el-option>
                            </el-select>
                        </el-form-item>
                        
                        <el-form-item v-if="isVideoSelected && selectedVideoInfo" label="视频信息">
                            <el-card class="video-info-card">
                                <template #header>
                                    <div class="video-info-header">
                                        <span>{{ formData.video_file_path.split('/').pop() }}</span>
                                        <el-tag type="success" size="small">已选择</el-tag>
                                    </div>
                                </template>
                                <div class="video-info-content">
                                    <el-descriptions :column="2" border>
                                        <el-descriptions-item label="分辨率">{{ selectedVideoInfo.resolution }}</el-descriptions-item>
                                        <el-descriptions-item label="帧率">{{ selectedVideoInfo.fps }} fps</el-descriptions-item>
                                        <el-descriptions-item label="总帧数">{{ selectedVideoInfo.total_frames }}</el-descriptions-item>
                                    </el-descriptions>
                                </div>
                            </el-card>
                        </el-form-item>
                    </div>
                    
                    <div class="form-section">
                        <h2 class="form-section-title">基本参数</h2>
                        
                        <el-form-item label="保存文件夹" prop="save_folder">
                            <el-input v-model="formData.save_folder" placeholder="请输入保存文件夹路径"></el-input>
                        </el-form-item>
                        
                        <el-form-item label="是否为泥石流" prop="is_debrisflow">
                            <el-radio-group v-model="formData.is_debrisflow">
                                <el-radio :label="true">是</el-radio>
                                <el-radio :label="false">否</el-radio>
                            </el-radio-group>
                        </el-form-item>
                        
                        <el-form-item label="数据类型" prop="data_type">
                            <el-select v-model="formData.data_type" placeholder="请选择数据类型">
                                <el-option label="训练集" value="train"></el-option>
                                <el-option label="验证集" value="val"></el-option>
                                <el-option label="测试集" value="test"></el-option>
                            </el-select>
                        </el-form-item>
                        
                        <el-form-item label="处理模式">
                            <el-radio-group v-model="formData.batch_mode">
                                <el-radio :label="false">单帧模式</el-radio>
                                <el-radio :label="true">批处理模式</el-radio>
                            </el-radio-group>
                        </el-form-item>
                        
                        <template v-if="!formData.batch_mode">
                            <el-form-item label="帧索引" prop="frame_idx">
                                <el-input-number 
                                    v-model="formData.frame_idx" 
                                    :min="0" 
                                    :max="selectedVideoInfo ? selectedVideoInfo.total_frames - 1 : undefined"
                                    placeholder="请输入帧索引"
                                ></el-input-number>
                                <span v-if="selectedVideoInfo" class="param-hint">
                                    (有效范围: 0 - {{ selectedVideoInfo.total_frames - 1 }})
                                </span>
                            </el-form-item>
                        </template>
                        
                        <template v-else>
                            <el-form-item label="起始帧" prop="batch_start_frame">
                                <el-input-number 
                                    v-model="formData.batch_start_frame" 
                                    :min="0" 
                                    :max="selectedVideoInfo ? selectedVideoInfo.total_frames - 1 : undefined"
                                    placeholder="请输入起始帧"
                                ></el-input-number>
                                <span v-if="selectedVideoInfo" class="param-hint">
                                    (有效范围: 0 - {{ selectedVideoInfo.total_frames - 1 }})
                                </span>
                            </el-form-item>
                            
                            <el-form-item label="结束帧" prop="batch_end_frame">
                                <el-input-number 
                                    v-model="formData.batch_end_frame" 
                                    :min="0" 
                                    :max="selectedVideoInfo ? selectedVideoInfo.total_frames - 1 : undefined"
                                    placeholder="请输入结束帧"
                                ></el-input-number>
                                <span v-if="selectedVideoInfo" class="param-hint">
                                    (有效范围: 0 - {{ selectedVideoInfo.total_frames - 1 }})
                                </span>
                            </el-form-item>
                            
                            <el-form-item label="步长" prop="batch_step">
                                <el-input-number 
                                    v-model="formData.batch_step" 
                                    :min="1" 
                                    placeholder="处理帧间隔"
                                ></el-input-number>
                                <span class="param-hint">
                                    (每隔多少帧处理一次)
                                </span>
                            </el-form-item>
                            
                            <el-form-item>
                                <el-alert
                                    type="info"
                                    :closable="false"
                                    show-icon
                                >
                                    <div>
                                        将处理从帧 <b>{{ formData.batch_start_frame }}</b> 到帧 <b>{{ formData.batch_end_frame }}</b> 之间，
                                        每隔 <b>{{ formData.batch_step }}</b> 帧的视频片段，
                                        预计生成 <b>{{ Math.ceil((formData.batch_end_frame - formData.batch_start_frame + 1) / formData.batch_step) }}</b> 个数据集。
                                    </div>
                                </el-alert>
                            </el-form-item>
                        </template>
                        
                        <el-form-item label="切片窗口大小" prop="slice_windows_size">
                            <el-input-number v-model="formData.slice_windows_size" :min="1" placeholder="请输入切片窗口大小"></el-input-number>
                        </el-form-item>
                        
                        <el-form-item label="提取频率" prop="extract_freq">
                            <el-input-number v-model="formData.extract_freq" :min="1" placeholder="请输入提取频率"></el-input-number>
                        </el-form-item>
                        
                        <el-form-item v-if="isVideoSelected && frameImages.start_frame" label="帧预览">
                            <div class="frames-preview">
                                <div class="frame-container">
                                    <div class="frame-title">
                                        <span v-if="formData.batch_mode">批处理起始帧 ({{ formData.batch_start_frame }})</span>
                                        <span v-else>起始帧 ({{ frameImages.start_idx }})</span>
                                    </div>
                                    <div class="frame-image-wrapper">
                                        <img 
                                            :src="'data:image/jpeg;base64,' + frameImages.start_frame" 
                                            alt="起始帧" 
                                            class="frame-image"
                                            ref="startFrameImg"
                                            @click="(e) => selectPointOnImage(e, $refs.startFrameImg)"
                                        />
                                        <div class="frame-overlay">点击选择兴趣点</div>
                                    </div>
                                </div>
                                <div class="frame-container">
                                    <div class="frame-title">
                                        <span v-if="formData.batch_mode">批处理结束帧 ({{ formData.batch_end_frame }})</span>
                                        <span v-else>中心帧/结束帧 ({{ frameImages.end_idx }})</span>
                                    </div>
                                    <div class="frame-image-wrapper">
                                        <img 
                                            :src="'data:image/jpeg;base64,' + frameImages.end_frame" 
                                            alt="结束帧" 
                                            class="frame-image"
                                            ref="endFrameImg"
                                            @click="(e) => selectPointOnImage(e, $refs.endFrameImg)"
                                        />
                                        <div class="frame-overlay">点击选择兴趣点</div>
                                    </div>
                                </div>
                                <div class="frames-info">
                                    <p v-if="formData.batch_mode">批处理范围：从帧 {{ formData.batch_start_frame }} 到帧 {{ formData.batch_end_frame }}，步长 {{ formData.batch_step }}</p>
                                    <p v-else>切片视频范围：从帧 {{ frameImages.start_idx }} 到帧 {{ frameImages.end_idx }}（共 {{ frameImages.end_idx - frameImages.start_idx + 1 }} 帧）</p>
                                    <el-button type="primary" size="small" @click="loadFrameImages" :loading="isLoadingFrames">
                                        刷新帧图像
                                    </el-button>
                                </div>
                            </div>
                        </el-form-item>
                        
                        <el-form-item label="兴趣点坐标" prop="point_coordinates">
                            <div class="points-container">
                                <!-- 批量输入 -->
                                <div class="coordinates-input">
                                    <el-input
                                        type="textarea"
                                        v-model="coordinatesText"
                                        :rows="3"
                                        placeholder="格式：[[x1,y1],[x2,y2],...] 示例：[[800,700],[1459,486]]"
                                        class="wide-textarea"
                                    ></el-input>
                                </div>

                                <!-- 单点输入 -->
                                <div class="single-point-input">
                                    <div class="point-inputs">
                                        <el-input-number
                                            v-model="newPoint.x"
                                            :min="0"
                                            class="point-coord-input"
                                            placeholder="X坐标"
                                        ></el-input-number>
                                        <el-input-number
                                            v-model="newPoint.y"
                                            :min="0"
                                            class="point-coord-input"
                                            placeholder="Y坐标"
                                        ></el-input-number>
                                        <el-button type="primary" @click="addSinglePoint">添加坐标点</el-button>
                                    </div>
                                </div>

                                <!-- 点列表 -->
                                <div class="points-list" v-if="formData.point_coordinates.length > 0">
                                    <div class="points-list-header">
                                        <span class="points-list-title">已添加的坐标点列表</span>
                                    </div>
                                    <div class="points-grid">
                                        <div v-for="(point, index) in formData.point_coordinates" :key="index" class="point-item">
                                            <el-input-number
                                                v-model="point[0]"
                                                :min="0"
                                                class="point-coord-input"
                                                placeholder="X坐标"
                                            ></el-input-number>
                                            <el-input-number
                                                v-model="point[1]"
                                                :min="0"
                                                class="point-coord-input"
                                                placeholder="Y坐标"
                                            ></el-input-number>
                                            <el-button type="danger" size="small" circle @click="removePoint(index)">
                                                <el-icon><Delete /></el-icon>
                                            </el-button>
                                        </div>
                                    </div>
                                    <div class="clear-points-container">
                                        <el-button type="danger" plain @click="clearPoints" class="clear-btn">清空所有点</el-button>
                                    </div>
                                </div>
                            </div>
                        </el-form-item>
                    </div>
                    
                    <div class="form-section">
                        <h2 class="form-section-title">SAM参数</h2>
                        
                        <el-form-item label="启用SAM视频处理" prop="sam_video_sign">
                            <el-switch v-model="formData.sam_video_sign"></el-switch>
                        </el-form-item>
                        
                        <template v-if="formData.sam_video_sign">
                            <el-form-item label="SAM模型类型" prop="sam_model_type">
                                <el-select v-model="formData.sam_model_type" placeholder="请选择SAM模型类型">
                                    <el-option label="vit_h (高精度)" value="vit_h"></el-option>
                                    <el-option label="vit_l (大型)" value="vit_l"></el-option>
                                    <el-option label="vit_b (基础)" value="vit_b"></el-option>
                                </el-select>
                            </el-form-item>
                            
                            <el-form-item label="运行设备" prop="sam_model_device">
                                <el-select v-model="formData.sam_model_device" placeholder="请选择运行设备">
                                    <el-option label="自动选择" value="auto"></el-option>
                                    <el-option label="CPU" value="cpu"></el-option>
                                    <el-option label="CUDA (GPU)" value="cuda"></el-option>
                                </el-select>
                            </el-form-item>
                            
                            <el-form-item label="SAM模型路径" prop="sam_checkpoint">
                                <el-input v-model="formData.sam_checkpoint" placeholder="请输入SAM模型权重文件路径"></el-input>
                            </el-form-item>
                        </template>
                    </div>
                    
                    <div class="form-actions">
                        <el-button type="primary" @click="submitForm" :disabled="!isVideoSelected || isProcessing">
                            开始处理
                        </el-button>
                        <el-button @click="resetForm">重置</el-button>
                    </div>
                </el-form>
                
                <div v-if="processResult" class="result-container">
                    <h3>处理结果</h3>
                    <el-alert
                        :title="processResult.message"
                        type="success"
                        :closable="false"
                        show-icon
                    ></el-alert>
                    
                    <!-- 批处理结果详细信息 -->
                    <div v-if="formData.batch_mode && processResult.results" class="batch-results">
                        <h4>批处理详细结果</h4>
                        <el-table :data="processResult.results" stripe style="width: 100%">
                            <el-table-column prop="frame_idx" label="帧索引" width="100"></el-table-column>
                            <el-table-column prop="success" label="状态">
                                <template #default="scope">
                                    <el-tag :type="scope.row.success ? 'success' : 'danger'">
                                        {{ scope.row.success ? '成功' : '失败' }}
                                    </el-tag>
                                </template>
                            </el-table-column>
                            <el-table-column label="详细信息">
                                <template #default="scope">
                                    <span v-if="scope.row.success">
                                        保存到: {{ scope.row.save_folder }}
                                    </span>
                                    <span v-else class="error-message">
                                        错误: {{ scope.row.error }}
                                    </span>
                                </template>
                            </el-table-column>
                        </el-table>
                    </div>
                </div>
            </el-card>
        </div>
    </div>
    `,
    computed: {
        formRules() {
            return {
                save_folder: [
                    { required: true, message: '请输入保存文件夹路径', trigger: 'blur' }
                ],
                video_file_path: [
                    { required: true, message: '请选择或上传视频', trigger: 'change' }
                ],
                frame_idx: [
                    { required: true, message: '请输入帧索引', trigger: 'blur' }
                ]
            };
        }
    }
});

// 使用Element Plus
app.use(ElementPlus);

// 注册所有图标
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
    app.component(key, component);
}

// 挂载应用
app.mount('#app'); 