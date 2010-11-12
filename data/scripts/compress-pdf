#! /bin/bash

# AUTHOR:	(c) Ricardo Ferreira
# NAME:		Compress PDF 1.4
# DESCRIPTION:	A nice Nautilus script with a GUI to compress and optimize PDF files
# REQUIRES:	ghostscript, poppler-utils, zenity
# LICENSE:	GNU GPL v3 (http://www.gnu.org/licenses/gpl.html)
# WEBSITE:	https://launchpad.net/compress-pdf

# Messages
		# English (en-US)
		error_nofiles="No file selected."
		error_noquality="No optimization level selected."
		error_ghostscript="PDF Compress requires the ghostscript package, which is not installed. Please install it and try again."
		error_nopdf="The selected file is not a valid PDF archive."
		label_filename="Save PDF as..."
		label_level="Please choose an optimization level below."
		optimization_level="Optimization Level"
		level_default="Default"
		level_screen="Screen-view only"
		level_low="Low Quality"
		level_high="High Quality"
		level_color="High Quality (Color Preserving)"
		job_done="has been successfully compressed"

case $LANG in

	pt* )
		# Portuguese (pt-PT)
		error_nofiles="Nenhum ficheiro seleccionado."
		error_noquality="Nenhum nível de optimização escolhido."
		error_ghostscript="O PDF Compress necessita do pacote ghostscript, que não está instalado. Por favor instale-o e tente novamente."
		error_nopdf="O ficheiro seleccionado não é um ficheiro PDF válido."
		label_filename="Guardar PDF como..."
		label_level="Por favor escolha um nível de optimização abaixo."
		optimization_level="Nível de Optimização"
		level_default="Normal"
		level_screen="Visualização no Ecrã"
		level_low="Baixa Qualidade"
		level_high="Alta Qualidade"
		level_color="Alta Qualidade (Preservação de Cores)"
		job_done="foi comprimido com sucesso";;


	es* )
		# Spanish (es-AR) by Eduardo Battaglia
		error_nofiles="Ningún archivo seleccionado."
		error_noquality="Ningún nivel de optimización escogido."
		error_ghostscript="Compress PDF necesita el paquete ghostscript, que no está instalado. Por favor instálelo e intente nuevamente."
		label_filename="Guardar PDF como..."
		label_level="Por favor escoja un nivel de optimización debajo."
		optimization_level="Nivel de Optimización"
		level_default="Normal"
		level_screen="Sólo visualización"
		level_low="Baja calidad"
		level_high="Alta calidad"
		level_color="Alta calidad (Preservación de Colores)";;


	cs*)
﻿		# Czech (cz-CZ) by Martin Pavlík
		error_nofiles="Nebyl vybrán žádný soubor."
		error_noquality="Nebyla zvolena úroveň optimalizace."
		error_ghostscript="PDF Compress vyžaduje balíček ghostscript, který není nainstalován. Nainstalujte jej prosím a opakujte akci."
		label_filename="Uložit PDF jako..."
		label_level="Prosím vyberte úroveň optimalizace z níže uvedených."
		optimization_level="Úroveň optimalizace"
		level_default="Výchozí"
		level_screen="Pouze pro čtení na obrazovce"
		level_low="Nízká kvalita"
		level_high="Vysoká kvalita"
		level_color="Vysoká kvalita (se zachováním barev)";;


	fr*)
﻿		# French (fr-FR) by Astromb
		error_nofiles="Aucun fichier sélectionné"
		error_noquality="Aucun niveau d'optimisation sélectionné"
		error_ghostscript="PDF Compress a besoin du paquet ghostscript, mais il n'est pas installé. Merci de l'installer et d'essayer à nouveau."
		error_nopdf="Le fichier que vous avez sélectionné n'est pas un PDF valide."
		label_filename="Sauvegarder le PDF sous..."
		label_level="Merci de choisir, ci-dessous, un niveau d'optimisation."
		optimization_level="Niveau d'optimisation"
		level_default="Défaut"
		level_screen="Affichage à l'écran"
		level_low="Basse qualité"
		level_high="Haute qualité"
		level_color="Haute qualité (Couleurs préservées)";;

	zh_CN*)
		# Simplified Chinese  (zh_CN) by TualatriX Chou
		error_nofiles="没有选择文件。"
		error_noquality="没有优化优化等级。"
		error_ghostscript="PDF压缩需要ghostscript软件包，但是它没有安装。请先安装然后再重试。"
		error_nopdf="选择的文件不是一个有效的PDF文件"
		label_filename="另存为PDF..."
		label_level="请在下面选择优化等级"
		optimization_level="优化等级"
		level_default="默认"
		level_screen="仅在屏幕上浏览"
		level_low="低品质"
		level_high="高品质"
		level_color="高品质（护色） ";;

        ar*)
                # Arabic (ar) by Mohammed hasan Taha
		error_nofiles="لم يتم اختيار ملف"
		error_noquality="لم يتم اختيار درجة الضغط"
		error_ghostscript="هذا السكربت يحتاج حزمة ghostscript package لذا يرجى تنصيبها ثم اعادة المحاولة"
		error_nopdf="الملف الذي تم اختياره ليس ملف pdf  صالح"
		label_filename="حفظ الملف باسم"
		label_level="الرجاء اختيار درجة الضغط"
		optimization_level="درجة الضغط"
		level_default="افتراضي"
		level_screen="عرض للشاشة فقط(الدرجة الأكثر انخفاضا)"
		level_low="جودة منخفضة"
		level_high="جودة مرتفعة"
		level_color="جودة عالية جدا";;

	ml_IN*)
		# Malayalam (ml_IN) by Hrishikesh K B
		error_nofiles="ഒരു ഫയലും  തിരഞ്ഞെടുത്തിട്ടില്ല."
		error_noquality="യാതൊരു ഒപ്റ്റിമൈസേഷന്‍ ലെവലും  തിരഞ്ഞെടുത്തിട്ടില്ല."
		error_ghostscript="പി ഡി എഫ് കംപ്രസ്സറിന് ഗോസ്റ്റ് സ്ക്രിപ്റ്റ് പാക്കേജ് ആവശ്യമാണ്. ആ പാക്കേജ് ഇന്‍സ്റ്റാള്‍ ചെയ്‌‌ത ശേഷം  ദയവായി വീണ്ടും  ശ്രമിക്കുക."
		error_nopdf="തിരഞ്ഞെടുത്ത ഫയല്‍ സാധുവായ ഒരു പിഡിഎഫ് ആര്‍ച്ചീവ് അല്ല."
		label_filename="പിഡിഎഫ് ഇങ്ങിനെ സംരക്ഷിക്കുക..."
		label_level="ദയവായി താഴെ നിന്നും  ഒരു ഒപ്റ്റിമൈസേഷന്‍ ലെവല്‍ തിരഞ്ഞെടുക്കുക."
		optimization_level="ഒപ്റ്റിമൈസേഷന്‍ ലെവല്‍ "
		level_default="ഡീഫാള്‍ട്ട്"
		level_screen="സ്ക്രീനില്‍ കാണാന്‍ മാത്രം  "
		level_low="കുറഞ്ഞ നിലവാരം"
		level_high="കൂടിയ നിലവാരം "
		level_color="കൂടിയ നിലവാരം (നിറം  സംരക്ഷിച്ചിട്ടുള്ളത്)"

esac

VERSION="1.4"
ZENITY=$(which zenity)

pdf_file=$(basename "$1")

# Check if Ghostscript is installed
GS="/usr/bin/ghostscript"
if [ ! -x $GS ]; then
        $ZENITY --error --title="Compress PDF "$VERSION"" --text="$error_ghostscript"
        exit 0;
fi

# Check if the user has selected any files
if [ -z "$NAUTILUS_SCRIPT_SELECTED_FILE_PATHS" ]; then
        $ZENITY --error --title="Compress PDF "$VERSION"" --text="$error_nofiles"
        exit 0;
fi

# Check if the selected file is a PDF
mimetype=$(file -b -i "$1")
if [ -z "`echo $mimetype | grep -i 'pdf' `" ]; then
	$ZENITY --error --title="Compress PDF "$VERSION"" --text="$error_nopdf"
        exit 0;
fi

# Ask the user to select a compressing format
selected_level=$($ZENITY  --list  --title="Compress PDF "$VERSION"" --text "$label_level" --radiolist  --column "" --column "$optimization_level" TRUE "$level_default" FALSE "$level_screen" FALSE "$level_low" FALSE "$level_high" FALSE "$level_color")
if [ -z "$selected_level" ]; then
        $ZENITY --error --title="Compress PDF "$VERSION"" --text="$error_noquality"
        exit 0;
fi

# Select the optimization level to use
case $selected_level in
        "$level_default")
                COMP_COMMAND="/default"
        ;;
        "$level_screen")
                COMP_COMMAND="/screen"
        ;;
        "$level_low")
                COMP_COMMAND="/ebook"
        ;;
        "$level_high")
                COMP_COMMAND="/printer"
        ;;
        "$level_color")
                COMP_COMMAND="/prepress"
        ;;
esac

# Choose output file name
temp_filename=.temp-"$pdf_file"
suggested_filename=compressed-"$pdf_file"
output_filename=$($ZENITY --file-selection --save --confirm-overwrite --filename="$suggested_filename" --title="$label_filename")

if [ "$?" = 1 ] ; then
        exit 0;
fi

# Extract metadata from the original PDF
pdfinfo "$1" | sed -e 's/^ *//;s/ *$//;s/ \{1,\}/ /g' -e 's/^/  \//' -e '/CreationDate/,$d' -e 's/$/)/' -e 's/: / (/' > .pdfmarks
sed -i '1s/^ /[/' .pdfmarks
sed -i '/:)$/d' .pdfmarks
echo "  /DOCINFO pdfmark" >> .pdfmarks

# Execute ghostscript while showing a progress bar
(echo "0" ;
 gs -sDEVICE=pdfwrite -dCompatibilityLevel=1.4 -dPDFSETTINGS=$COMP_COMMAND -dNOPAUSE -dQUIET -dBATCH -sOutputFile="$temp_filename" "$1" .pdfmarks
 rm .pdfmarks
 echo "100") | (if `$ZENITY --progress --pulsate --auto-close --title="Compress PDF "$VERSION""`;
                 then
                     mv -f "$temp_filename" "$output_filename" &
                     notify-send "Compress PDF" "$pdf_file $job_done"
                 else
                     killall gs
                     rm "$temp_filename"
                     exit
                 fi)
