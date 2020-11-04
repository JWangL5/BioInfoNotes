setwd("F:/Rcode")

install.packages("devtools")
require(devtools)
install.packages("F:\\Rcode\\RFile\\dbplyr_1.4.4.tar.gz")

# 下载chipseqDB
if (!requireNamespace("BiocManager", quietly = TRUE))
  install.packages("BiocManager")
BiocManager::install("chipseqDB")

# ----------------------------------------------------------------------------
# 下载案例数据
BiocManager::install("chipseqDBData")

# 载入数据（可能由于网络原因下载失败）
# 下载的数据包含Bam文件和对应文件名的bai文件（BAM的索引）
library(chipseqDBData)
acdata <- H3K9acData()
acdata

# Rsamtools是一个读BAM格式文件的工具
BiocManager::install("Rsamtools")
library(Rsamtools)


# 将数据读入并描述统计
diagnostics <- list()
for (b in seq_along(acdata$Path)) {
  bam <- acdata$Path[[b]]
  total <- countBam(bam)$records
  mapped <- countBam(bam, param=ScanBamParam(
    flag=scanBamFlag(isUnmapped=FALSE)))$records
  marked <- countBam(bam, param=ScanBamParam(
    flag=scanBamFlag(isUnmapped=FALSE, isDuplicate=TRUE)))$records
  diagnostics[[b]] <- c(Total=total, Mapped=mapped, Marked=marked)
}
# 将数据整理为DataFrame的形式
diag.stats <- data.frame(do.call(rbind, diagnostics))
rownames(diag.stats) <- acdata$Name
# 统计百分比
diag.stats$Prop.mapped <- diag.stats$Mapped/diag.stats$Total*100
diag.stats$Prop.marked <- diag.stats$Marked/diag.stats$Mapped*100

diag.stats
# Ideally, the proportion of mapped reads should be high (70-80% or higher), 
# while the proportion of marked reads should be low (generally below 20%).

# ----------------------------------------------------------------------------

# 去除噪声，方法是和黑名单比对然后剔除，首先需要下载黑名单

BiocManager::install("BiocFileCache")
library(dbplyr)
library(BiocFileCache)

# 这个官网的代码实际测试有问题
# "filter_"没有适用于"c('tbl_SQLiteConnection', 'tbl_dbi', 'tbl_sql', 'tbl_lazy', 'tbl')"目标对象的方
bfc <- BiocFileCache("local", ask=FALSE)
black.path <- bfcrpath(bfc, file.path("https://www.encodeproject.org",
                                      "files/ENCFF547MET/@@download/ENCFF547MET.bed.gz"))
bfcr

# 选择手动下载数据
# https://www.encodeproject.org/files/ENCFF547MET/
# 这个是对照组的下载地址

# 使用rtracklayer的import方法导入该对照数据
BiocManager::install("rtracklayer")
library(rtracklayer)

blacklist <- import("F:\\Rcode\\RFile\\ENCFF547MET.bed.gz")
blacklist

# 在之后数据读取和分析中，忽略掉blacklst中的序列
# 设置minq，映射质量（MAPQ）得分低于20的同样删去
BiocManager::install("csaw")
library(csaw)
standard.chr <- paste0("chr", c(1:19, "X", "Y"))
param <- readParam(minq=20, discard=blacklist, restrict=standard.chr)

param

# ----------------------------------------------------------------------------
# 计算平均片段长度
# 免疫沉淀成功，则应在互相关中观察到一个强峰
# [QUESTION]

x <- correlateReads(acdata$Path, param=reform(param, dedup=TRUE))
frag.len <- maximizeCcf(x)
frag.len

plot(1:length(x)-1, x, xlab="Delay (bp)", ylab="CCF", type="l")
abline(v=frag.len, col="red")
text(x=frag.len, y=min(x), paste(frag.len, "bp"), pos=4, col="red")

# ----------------------------------------------------------------------------
# 对每个序列窗口进行计数，每150个bp为一个计数窗口

win.data <- windowCounts(acdata$Path, param=param, width=150, ext=frag.len)
win.data

# 计算背景丰度
# 在没有对照的时候，可以假设基因组的大部分位置都没有结合pro
# 因而背景的结合可以在更大的窗口上取中位数
bins <- windowCounts(acdata$Path, bin=TRUE, width=2000, param=param)
filter.stat <- filterWindowsGlobal(win.data, bins)
min.fc <- 3
keep <- filter.stat$filter > log2(min.fc) # 与1.54比大小
summary(keep)


hist(filter.stat$back.abundances, main="", breaks=50,
     xlab="Background abundance (log2-CPM)")
threshold <- filter.stat$abundances[1] - filter.stat$filter[1] + log2(min.fc)
abline(v=threshold, col="red")

filtered.data <- win.data[keep,]

