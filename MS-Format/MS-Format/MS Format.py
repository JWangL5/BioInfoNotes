import tkinter
from tkinter.ttk import Combobox
import tkinter.filedialog
import tkinter.messagebox
import xlwt
import xml.etree.ElementTree as ET
from io import StringIO
import pandas as pd
import requests

LOGO_PATH = 'ref/logo.png'
FGBN2CG_PATH = "ref/fbgn_annotation_ID_fb_2020_06.tsv"
FGPP2FGBN_PATH = "ref/fbgn_fbtr_fbpp_expanded_fb_2020_06.tsv"
GO_ANNO_PATH = "ref/gene_association_v2.2.fb"
GO_ITEM_PATH = 'ref/go.obo'
GO_ITEM_CSV_PATH = 'ref/go.csv'
SNAPSHOT_PATH = 'ref/gene_snapshots_fb_2020_06.tsv'


def mzxmltoxls(path):
    tree = ET.ElementTree()
    tree.parse(path)
    mztag = "{http://www.matrixscience.com/xmlns/schema/mascot_search_results_2}"

    workbook = xlwt.Workbook(encoding='utf-8')
    booksheet1 = workbook.add_sheet('Protein', cell_overwrite_ok=False)
    booksheet2 = workbook.add_sheet('Peptide', cell_overwrite_ok=False)

    title1 = ['hit_number', 'accession', 'prot_desc', 'prot_score', 'prot_mass', \
              'prot_matches', 'prot_matches_sig', 'prot_sequences', 'prot_sequences_sig', \
              'prot_cover', 'prot_len', 'prot_pi', 'prot_seq']
    for index, item in enumerate(title1):
        booksheet1.write(0, index, item)

    title2 = ['protein_accession', 'querry', 'pep_exp_mz', 'pep_exp_mr', 'pep_exp_z',
              'pep_calc_mr', 'pep_delta', 'pep_miss', 'pep_score', 'pep_expect',
              'pep_res_before', 'pep_seq', 'pep_res_after', 'pep_var_mod',
              'pep_var_mod_pos', 'pep_summed_mod_pos', 'pep_scan_title']
    for index, item in enumerate(title2):
        booksheet2.write(0, index, item)

    hits = tree.find(mztag + 'hits')
    row1, row2 = 1, 1
    for hit in hits:
        hit_num = hit.attrib['number']
        for i in hit:
            accession = i.attrib['accession']
            booksheet1.write(row1, 0, hit_num)
            booksheet1.write(row1, 1, accession)
            for j in i:
                if j.tag.split('}')[1] == 'peptide': break
                if j.tag.split('}')[1] == 'prot_desc': booksheet1.write(row1, 2, j.text)
                if j.tag.split('}')[1] == 'prot_score': booksheet1.write(row1, 3, j.text)
                if j.tag.split('}')[1] == 'prot_mass': booksheet1.write(row1, 4, j.text)
                if j.tag.split('}')[1] == 'prot_matches': booksheet1.write(row1, 5, j.text)
                if j.tag.split('}')[1] == 'prot_matches_sig': booksheet1.write(row1, 6, j.text)
                if j.tag.split('}')[1] == 'prot_sequences': booksheet1.write(row1, 7, j.text)
                if j.tag.split('}')[1] == 'prot_sequences_sig': booksheet1.write(row1, 8, j.text)
                if j.tag.split('}')[1] == 'prot_cover': booksheet1.write(row1, 9, j.text)
                if j.tag.split('}')[1] == 'prot_len': booksheet1.write(row1, 10, j.text)
                if j.tag.split('}')[1] == 'prot_pi': booksheet1.write(row1, 11, j.text)
                if j.tag.split('}')[1] == 'prot_seq': booksheet1.write(row1, 12, j.text)
            row1 += 1

            for k in i.iterfind(mztag + 'peptide'):
                try:
                    query = k.attrib['query']
                except:
                    query = ""

                booksheet2.write(row2, 0, accession)
                booksheet2.write(row2, 1, query)
                for h in k:
                    if h.tag.split('}')[1] == 'pep_exp_mz': booksheet2.write(row2, 2, h.text)
                    if h.tag.split('}')[1] == 'pep_exp_mr': booksheet2.write(row2, 3, h.text)
                    if h.tag.split('}')[1] == 'pep_exp_z': booksheet2.write(row2, 4, h.text)
                    if h.tag.split('}')[1] == 'pep_calc_mr': booksheet2.write(row2, 5, h.text)
                    if h.tag.split('}')[1] == 'pep_delta': booksheet2.write(row2, 6, h.text)
                    if h.tag.split('}')[1] == 'pep_miss': booksheet2.write(row2, 7, h.text)
                    if h.tag.split('}')[1] == 'pep_score': booksheet2.write(row2, 8, h.text)
                    if h.tag.split('}')[1] == 'pep_expect': booksheet2.write(row2, 9, h.text)
                    if h.tag.split('}')[1] == 'pep_res_before': booksheet2.write(row2, 10, h.text)
                    if h.tag.split('}')[1] == 'pep_seq': booksheet2.write(row2, 11, h.text)
                    if h.tag.split('}')[1] == 'pep_res_after': booksheet2.write(row2, 12, h.text)
                    if h.tag.split('}')[1] == 'pep_var_mod': booksheet2.write(row2, 13, h.text)
                    if h.tag.split('}')[1] == 'pep_var_mod_pos': booksheet2.write(row2, 14, h.text)
                    if h.tag.split('}')[1] == 'pep_summed_mod_pos': booksheet2.write(row2, 15, h.text)
                    if h.tag.split('}')[1] == 'pep_scan_title': booksheet2.write(row2, 16, h.text)
                row2 += 1
    workbook.save(path.split('.')[0] + '.xls')
    return path.split('.')[0] + '.xls'


def getfromUniprot(accessions, go=True, path=None):
    res, n = [], 1888
    # https://www.uniprot.org/help/uniprotkb_column_names
    columns = ['id', 'protein names', 'genes', 'comment(FUNCTION)']
    if go:
        columns.append("go(biological process)")
        columns.append("go(molecular function)")
        columns.append("go(cellular component)")
    for i in range(0, len(accessions), n):
        url = 'https://www.uniprot.org/uploadlists/'
        response = requests.post(url,
                                 {'query': ' '.join(accessions[i:i + n]),
                                  'from': 'ACC+ID',
                                  'to': 'ACC',
                                  'columns': ','.join(columns),
                                  'format': 'tab'})
        res.append(pd.read_csv(StringIO(response.text), sep='\t'))
    result = pd.concat(res)
    if path:
        result.to_csv(path, index=False)
    return result


def getIDfromtxt(txtpath):
    genelst = []
    with open(txtpath) as f:
        for line in f:
            genelst.append(line.replace('\n', ''))
        f.close()
    return genelst


def fgbn2cg(genelst_path, path=None):
    genelst = getIDfromtxt(genelst_path)
    genes = pd.DataFrame(data=genelst, columns=['primary_FBgn#'])
    fgbn2cg = pd.read_csv(FGBN2CG_PATH, sep='\t', skiprows=4)
    result = pd.merge(genes, fgbn2cg[['##gene_symbol', 'annotation_ID', 'primary_FBgn#']], on=['primary_FBgn#'])
    if path:
        result.to_csv(path, index=False)
    result.to_csv(path, encoding='utf_8_sig')
    return result


def fgpp2cg(pro_lst, path=None):
    genes = pd.DataFrame(data=pro_lst, columns=['polypeptide_ID'])
    fgbn2cg = pd.read_csv(FGPP2FGBN_PATH, sep='\t', skiprows=4, encoding='utf8')
    result = pd.merge(genes, fgbn2cg[['polypeptide_symbol', 'annotation_ID', 'gene_ID', 'polypeptide_ID']],
                      on=['polypeptide_ID'])
    if path:
        result.to_csv(path, index=False)
    return result


def go_search_flybase(gene_lst, path=None):
    go_search = []
    with open(GO_ANNO_PATH) as f:
        for line in f:
            if line.startswith('FB'):
                lsp = line.split('\t')
                if lsp[1] in gene_lst:
                    go_search.append([lsp[1], lsp[3], lsp[4]])

    search = pd.DataFrame(data=go_search, columns=["FlybaseID", "Process", "GO_id"])
    try:
        goterm = pd.read_csv(GO_ITEM_CSV_PATH)
    except:
        goterm = createGOitem()
    res1 = pd.merge(search, goterm, on=['GO_id'])
    res2 = res1.groupby(by=['FlybaseID', 'GO_kind'])['GO_name'].apply(lambda x: x.str.cat(sep=',')).reset_index()
    df = pd.Series(list(res2['GO_name']), index=[res2['FlybaseID'], res2['GO_kind']]).unstack()
    if path:
        df.to_csv(path)
    return df


def createGOitem():
    f = open(GO_ITEM_PATH)
    res = []
    a = []
    for line in f:
        if line.startswith('id:'):
            try:
                res.append(a)
            except:
                pass
            a = [line[4:].replace('\n', '')]
        if line.startswith('name'):
            a.append(line.split(': ')[1].replace('\n', ''))
    f.close()

    go = pd.DataFrame(data=res, columns=['GO_id', 'GO_name', 'GO_kind'])
    go.to_csv('ref/go.csv')
    return go


def getSnapshot(gene_lst, path):
    genes = pd.DataFrame(data=gene_lst, columns=['##FBgn_ID'])
    snapshotinfo = pd.read_csv(SNAPSHOT_PATH, sep='\t', skiprows=4, encoding='utf8')
    result = pd.merge(genes, snapshotinfo, on='##FBgn_ID', how='left')
    result = result.drop_duplicates(keep="first")
    if path:
        result.to_csv(path, index=False)
    return result


class MainForm:
    DB = ['Uniport_HUMAN', 'FlyBase']

    def __init__(self):
        self.xmlpath = ''
        root = tkinter.Tk()
        root.title("MS-Format by FuLab")
        # root.iconbitmap(LOGO_PATH)
        root.iconphoto(False, tkinter.PhotoImage(file=LOGO_PATH))
        root.geometry(f"500x200+{int((root.winfo_screenwidth()-500)/2)}+{int((root.winfo_screenheight()-400)/2)}")
        root.resizable(width=False, height=False)

        tkinter.Label(root, text="Mascot Database:", font=("等线",12)).place(x=30, y=40)
        tkinter.Label(root, text="XML File Path:", font=("dengxian",12)).place(x=35, y=80)

        self.dbvar = tkinter.StringVar()
        combox_db = Combobox(root,textvariable=self.dbvar, width=28,values=self.DB,state='readonly')
        combox_db.current(0)
        combox_db.place(x=195, y=42)

        self.entry_filepath = tkinter.Entry(root, width=24)
        self.entry_filepath.place(x=195, y=82)
        tkinter.Button(root, text='选择', command=self.getafile).place(x=430, y=78)

        # self.pb = Progressbar(root)
        # self.pb.place(x=32, y=140, width=350)

        button_confirm = tkinter.Button(root, text="开始", command=self.process)
        # button_confirm.bind("<Button-1>", lambda event:self.process(event))
        button_confirm.place(x=430, y=135)

        root.mainloop()

    def getafile(self):
        self.xmlpath = tkinter.filedialog.askopenfilename()
        self.entry_filepath.delete(0, "end")
        self.entry_filepath.insert(0,self.xmlpath)

    def process(self):
        XML_PATH = self.xmlpath
        if self.xmlpath=="":
            return tkinter.messagebox.showerror("错误", "请选择XML文件")

        if self.dbvar.get()=="Uniport_HUMAN":
            XLS_PATH = mzxmltoxls(XML_PATH)
            data = pd.read_excel(XLS_PATH, sheet_name="Protein")
            data['UniProt_Accession'] = data['accession'].apply(lambda x: x.split('::')[-1])
            try:
                go = pd.read_csv(XML_PATH.split('.')[0] + "_GOSearch.csv")
            except:
                go = getfromUniprot(data['UniProt_Accession'].tolist(),
                                                  path=XML_PATH.split('.')[0] + "_GOSearch.csv")

            result = pd.DataFrame(data[['hit_number', 'UniProt_Accession', 'prot_score', 'prot_mass', 'prot_matches_sig']])
            result.columns = ['hit#', 'Accession', 'score', 'mass', '#of peptides']
            try:
                result = pd.merge(result, go, left_on='Accession', right_on='Entry', how='left')
            except:
                return tkinter.messagebox.showwarning(title="Warning", message="请检查Database!")
            result = result[['hit#', 'Accession', 'score', 'mass', '#of peptides', 'Gene names',
                             'Protein names', 'Function [CC]', 'Gene ontology (biological process)',
                             'Gene ontology (molecular function)', 'Gene ontology (cellular component)']]
            result = result.dropna(subset=["Protein names", "Gene names"])
            result.to_csv(XML_PATH.split('.')[0] + "_fomated.csv", index=False, encoding = 'utf_8_sig')
            return tkinter.messagebox.showinfo(title="成功", message="转换成功！")

        if self.dbvar.get()=="FlyBase":
            try:
                data = pd.read_excel(XML_PATH.split('.')[0] + ".xls")
            except:
                XLS_PATH = mzxmltoxls(XML_PATH)
                data = pd.read_excel(XLS_PATH, sheet_name="Protein")

            data['DataBase'] = data['accession'].apply(lambda x: x.split('::')[0])
            data = data[data['DataBase'] != "1"]
            data['FBpp'] = data['accession'].apply(lambda x: x.split('::')[-1])

            try:
                cg = pd.read_csv(XML_PATH.split('.')[0] + '_cg.csv')
            except:
                prolst = data['FBpp'].tolist()
                cg = fgpp2cg(prolst, path=XML_PATH.split('.')[0] + '_cg.csv')
            result = pd.merge(data, cg, how='left', left_on='FBpp', right_on='polypeptide_ID')

            try:
                go = pd.read_csv(XML_PATH.split('.')[0] + '_GOSearch.csv')
            except:
                go = go_search_flybase(result['gene_ID'].tolist(),
                                                     path=XML_PATH.split('.')[0] + '_GOSearch.csv')
            result = pd.merge(result, go, how='left', left_on='gene_ID', right_on='FlybaseID')

            try:
                snapshot = pd.read_csv(XML_PATH.split('.')[0] + '_snapshot.csv')
            except:
                snapshot = getSnapshot(result['gene_ID'].tolist(),
                                                     path=XML_PATH.split('.')[0] + '_snapshot.csv')
            result = pd.merge(result, snapshot, how='left', left_on='gene_ID', right_on='##FBgn_ID')

            result = pd.DataFrame(
                result[['annotation_ID', 'polypeptide_symbol', 'prot_score', 'prot_mass', 'prot_matches_sig',
                        'prot_sequences_sig', 'prot_cover', 'biological_process', 'cellular_component',
                        'molecular_function',
                        'gene_snapshot_text']])
            result.columns = ['CG', 'Protein name', 'Score', 'Mass', '#of spectrum', '#of peptides', 'coverage',
                              'biological_process',
                              'cellular_component', 'molecular_function', 'snapshot']
            result = result.sort_values(by=['Score', '#of spectrum'], ascending=[False, False])
            result.to_csv(XML_PATH.split('.')[0] + '_formated.csv', index=False, encoding = 'utf_8_sig')
            return tkinter.messagebox.showinfo(title="成功", message="转换成功！")


def main():
    MainForm()


if __name__ == '__main__':
    main()


